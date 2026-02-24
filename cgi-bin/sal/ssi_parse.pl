# This is a simple SSI parser written by Sam Owre; there are undoubtedly
# better ones out there, but I couldn't find them at the time this was
# written.

# It simply expands some of the SSI commands directly, as the html generated
# by a CGI script will not be processed by Apache.  It takes an html file
# and a file handler string as input, and writes to stdout.

# It currently handles #if, #elsif, #else, #endif, #set, #echo, and #include
# For all others it simply writes a complaint.

sub ssi_parse_and_output {
  local ($include_file, $input) = @_;
  $input++;
  open($input,"$include_file") || die "Can't open $include_file\n";
  while (<$input>) {
    s/\n$//;
    if (/<!--\#elsif expr=\"(.*)\" *-->/) {
      if (!$if_done) {
	if ($if_cond) {
	  $if_cond = 0;
	  $if_done = 1;
	}
	else {
	  $if_cond = eval "$1";
	}
      }
    }
    elsif (/<!--\#else *-->/) {
      if (!$if_done) {
	if ($if_cond) {
	  $if_cond = 0;
	  $if_done = 1;
	}
	else {
	  $if_cond = 1;
	}
      }
    }
    elsif (/<!--\#if expr=\"(.*)\" *-->/) {
      if ($in_if) {
	push(@if_stack, ($if_cond, $if_done));
      }
      $ssi_if = $&;
      $ssi_expr = $1;
      $ifcond = eval "$ssi_expr";
      $in_if = 1;
      $if_done = 0;
    }
    elsif (/<!--\#endif *-->/) {
      if (@if_stack) {
	($if_cond, $if_done) = pop(@if_stack);
	$in_if = 1;
      }
      else {
	$in_if = 0;
      }
    }
    elsif ($in_if && (!$if_cond || $if_done)) {
    }
    elsif (/<!--\#set *(var|value)=\"(.*)\" *(var|value)=\"(.*)\" *-->/) {
      ($1 eq 'var') ? $ssi_var = $2 : $ssi_value = $2;
      ($3 eq 'var') ? $ssi_var = $4 : $ssi_value = $4;
      # print "\nSetting $ssi_var to $ssi_value\n";
      $ssi_var_map{$ssi_var} = $ssi_value;
    }
    elsif (/<!--\#echo var=\"([^-]*)\" *-->/) {
      $ssi_var = $1;
      $rest = $&;
      s/$rest/$ssi_var_map{$ssi_var}/g;
      while (/<!--\#echo var=\"([^-]*)\" *-->/) {
	$ssi_var = $1;
	$rest = $&;
	s/$rest/$ssi_var_map{$ssi_var}/g;
      }
      print "$_\n";
    }
    elsif (/<!--\#include *(virtual|file)=\"(.*)\" *-->/) {
      ssi_parse_and_output($2, $input);
      next;
    }
    elsif (/<!--\#(.*) -->/) {
      $ssi_cmd = $1;
      print "Don't understand ssi command $ssi_cmd\n";
    }
    else {
      print "$_\n";
    }
  }
  close $input;
}

# Need to return true to satisfy the require - isn't PERL intuitive?
1;
