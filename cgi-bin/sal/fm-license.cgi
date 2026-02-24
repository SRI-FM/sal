#!/usr/bin/perl -w

# $Date: $
# $Id: $

# fm-license.cgi:
#
# PURPOSE:
#
#   Manage the FORM data for the FM license form.
#
# INPUTS:
#
#   The following data from the FORM...
#
#      Text parameter FORM, which names the Web page from which the
#         data come so this program knows which Web page to display
#         next, i.e., whether to display the data for the user to approve
#         or whether the user has already approved the data.  (For security
#         reasons the data are validated no matter where they come from.)
#
#      Radio button AGREETORESTRICTIONS (= "DO" or "DO NOT"), which
#         says whether the requester does/does not agree to the
#         licensing requirements.  For the FORM data to be processed, this
#         value must be "DO".
#
#      All (text) parameters in @RequiredParm below.
#
#   Files used to display new Web pages...
#      The file name is <name>.template, where <name> is defined in
#      the array %NextForm below and chosen based on the input value
#      of variable "FORM".  For example, if the program receives the data
#         param("FORM") = "application"
#      then the file used to display the output Web page will be
#         verification.template
#
# HOW TO ADD NEW FORM VARIABLES:
#
#   Text, required:
#      Add the name (anywhere) to the @RequiredParm definition.
#      Add appropriate text to the %ErrorText and %PromptText hashes.
#      Add the name to the end of the @parse_field definition.

use strict;
use Mail::Mailer;

# ---------------------------------------
# Use the standard perl library to handle forms data.  It gets parameter
# values and also does a lot of anti-hacker checking.  It handles either
# POST or GET <FORM ...> methods.
#    POST sends the data attached to the end of the httpd request.
#    GET encodes the data onto the URL.
# The "standard" CGI means NOT the object-oriented interface.
# ---------------------------------------
use CGI qw (:standard);

# ---------------------------------------
# Prevent POST-oriented denial of service attacks: buffer overflows
# and file uploads.
# ---------------------------------------
use CGI::Carp 'fatalsToBrowser';

my $create_signature = "/homes/web/sal.csl.sri.com/cgi-bin/create_signature";
my $csparams = "/homes/web/etc/csparams";

# ---------------------------------------
# Define required (text) variables.
# ---------------------------------------
my @RequiredParm = qw (
      REQUESTER
      INSTITUTION
      STREET
      CITY
      STATE
      ZIP
      COUNTRY
      PHONE
      EMAIL
   );

# ---------------------------------------
# Define text to be used in error messages.
# ---------------------------------------
my %ErrorText = (
      REQUESTER   => "name"
     ,INSTITUTION => "organization"
     ,EMAIL       => "email address"
     ,STREET      => "street or mailbox address"
     ,CITY        => "city"
     ,STATE       => "state/province"
     ,ZIP         => "ZIP Code"
     ,COUNTRY     => "country"
     ,PHONE       => "phone number"
     ,FORM        => "form input"
     ,SYSTEM      => "system (ICS or SAL)"
   );

# ---------------------------------------
# Define text to be used in acceptance message.
# ---------------------------------------
my %PromptText = (
      REQUESTER   => "Name:          "
     ,INSTITUTION => "Organization:  "
     ,EMAIL       => "Email Address: "
     ,STREET      => "Street/Mailbox:"
     ,CITY        => "City:          "
     ,STATE       => "State/Province:"
     ,ZIP         => "ZIP Code:      "
     ,COUNTRY     => "Country:       "
     ,PHONE       => "Phone number:  "
   );

# ---------------------------------------
# Define the acceptable radio button and "FORM=" values.  No other
# responses than these (or empty) will come from a valid form.
# ---------------------------------------
my @valid_FORM       = qw (application verification);
my @valid_SYSTEM     = qw (SAL ICS);

# ---------------------------------------
# Define the next HTML page to use as a function of the current one.
# ---------------------------------------
my %NextForm = (
   application  => "verification"
  ,verification => "final"
   );

# ---------------------------------------
# Define the fields to dump in the email for parsing.
# ---------------------------------------

my @parse_field = qw(
   AGREETORESTRICTIONS
   REQUESTER
   INSTITUTION
   STREET
   CITY
   STATE
   ZIP
   COUNTRY
   PHONE
   EMAIL
   SYSTEM
   timestamp
);

my %value;

my $start = (times)[0]; # used for calculating total execution time

# ---------------------------------------
# Define the path to sendmail on this web server.
# ---------------------------------------
my $SENDMAIL="/usr/sbin/sendmail";

$CGI::POST_MAX=1024 * 100;       # max 100K posts
$CGI::DISABLE_UPLOADS = 1;       # no uploads

# ---------------------------------------
# Compare the input form name to list of valid values.
# This tells the program whether to use the verification or final form.
# ---------------------------------------
$value{"FORM"} = param("FORM");
my $value_ok = 0;        # valid value has not yet been found
foreach my $valid_value ( @valid_FORM ) {
   if ( $value{"FORM"} eq $valid_value ) {
         $value_ok = 1;  # valid value has been found
   }
} # foreach value that is valid for this parameter
if ($value_ok) {
   $value{"FORM"} = $NextForm {$value{"FORM"} };
}
else {
   &IllegalChars ("FORM");
}

$value{"SYSTEM"} = param("SYSTEM");
my $value_ok = 0;        # valid value has not yet been found
foreach my $valid_value ( @valid_SYSTEM ) {
   if ( $value{"SYSTEM"} eq $valid_value ) {
         $value_ok = 1;  # valid value has been found
   }
} # foreach value that is valid for this parameter
if (!$value_ok) {
   &IllegalChars ("SYSTEM");
}

# ---------------------------------------
# Verify that the user has agreed to the license restrictions.
# ---------------------------------------
$value{"AGREETORESTRICTIONS"} = param("AGREETORESTRICTIONS");
if ( $value{"AGREETORESTRICTIONS"} ne "DO") {
   print "Content-type: text/html\n\n";
   print "
<HTML>
<HEAD>
<BODY BGCOLOR=\"#FFFFFF\">
<CENTER>
<BR>
<BR>
<BR>
<H3>
You must agree to the ";
   print $value{"SYSTEM"};
   print " license terms before your
registration request can be processed.
<BR><BR>
You may use the Back button on your browser to return to the registration form.
There you will find a link to the license agreement and a button
to click to agree to the terms.<BR>
</H3>
</CENTER>
</BODY>
</HTML>
";
   exit; ### Bail Out Here
} # User did not agree to license

# ---------------------------------------
# Verify that the user has not left any required fields blank.
# ---------------------------------------
$value{"COUNTRY"} = param("COUNTRY");
foreach my $variable ( @RequiredParm) {
   $value{$variable} = param ("$variable");

   $value{$variable} =~ s/^\s*//; # get rid of leading white space
   $value{$variable} =~ s/\s*$//; # get rid of trailing white space
   if ( $value{$variable} =~ /^\s*$/) {

# ---------------------------------------
# The STATE parameter is only required for USA entries.
# ---------------------------------------
      if ($variable ne "STATE" ||
          ($variable eq "STATE" &&
           $value{"COUNTRY"} !~ /[rR][aA][bB]/ &&
           $value{"COUNTRY"} =~ /^[tT]*[hH]*[eE]* *[uU].*[sS]/)) {

# ---------------------------------------
# Write error message for a blank field.  Standard out is back to the client.
# The first line must be the mime type; the second a blank line.  Otherwise
# the server does not send output back to the client.
# ---------------------------------------
         print "Content-type: text/html\n\n";
         print "
<HTML>
<HEAD>
<BODY BGCOLOR=\"#FFFFFF\">
<CENTER>
<BR>
<BR>
<BR>
<H3>
Your $ErrorText{$variable}, which is <font color=\"blue\">required</font>,
was not provided in your form.<BR><BR>
Please use the Back button on your browser to return to the form and complete it.<BR>
</H3>
</CENTER>
</BODY>
</HTML>
";
         exit; ### Bail Out Here; no input!
      }    
   }    

# ---------------------------------------
# Required field is not blank; save it.
# ---------------------------------------
   else {
      $value{$variable} =~ s/\s+/ /; # get rid of redundant white space
   }
} # foreach required variable.

my $s = "<BR>";

# ---------------------------------------
# Get the time for printing.
# ---------------------------------------
$value{"timestamp"} = scalar (localtime (time));

# ---------------------------------------
# Use an HTML template to echo user inputs.
# ---------------------------------------
&writeHTML ($value{"FORM"});

# ---------------------------------------
# The input data have been displayed.  If the client has done final
# submission, send the email
# ---------------------------------------

if ($value{"FORM"} eq "final") {
   my $mailer = Mail::Mailer->new("sendmail");
   $mailer->open ({ To      => "$value{\"EMAIL\"}",
                    From    => "$value{\"SYSTEM\"}" . '-sri@csl.sri.com',
                    Subject => "$value{\"SYSTEM\"} certificate for $value{\"REQUESTER\"}",
		    Bcc     => "$value{\"SYSTEM\"}" . '-registration@csl.sri.com',
                 })
      or 
         die ( "\n*********************************************************\n\nTemporary problem encountered: unable to send email.\nClick your browser's Reload button or use your browser's\nBack button to return to the preceeding page and try submitting it again.\n\nIf this problem recurs, please contact sal\@csl.sri.com.\n\n*********************************************************\n\n");

   print $mailer "On " , $value{timestamp},
   "\na request was received for a $value{\"SYSTEM\"} license certificate.\n";
   print $mailer "    From Remote Address: $ENV{'REMOTE_ADDR'}\n\n";
   if ( "$value{\"SYSTEM\"}" eq "SAL" ) {
     print $mailer "EITHER copy this mail message to '<SAL>/certificate', where\n",
     "<SAL> is where you installed the sal distribution,\nOR ";
   }
   else {
     print $mailer "Please ";
   }
   print $mailer "copy this mail message to a convenient location,\n",
   	"and set the global variable $value{\"SYSTEM\"}", "_LICENSE_CERTIFICATE to the\n",
   	"location of that file.  ";
   if ("$value{\"SYSTEM\"}" eq "SAL") {
     print $mailer "Also set the global variable\nICS_LICENSE_CERTIFICATE to this file, ",
     	  "if it is not already set\nto a file name with a valid certificate.\n";
   }
   print $mailer "Make certain not to modify anything between\n",
   	"the '# Beginning of signed message' and '# End of signed message'\n",
	"lines, inclusive.  For example, copy this message to '\$HOME/cert'\n",
        "and set ";
   if ("$value{\"SYSTEM\"}" eq "SAL") {
     print $mailer "SAL_LICENSE_CERTIFICATE and ICS_LICENSE_CERTIFICATE\nto '\$HOME/cert'.\n\n";
     }
   else {
     print $mailer "ICS_LICENSE_CERTIFICATE to '\$HOME/cert'.\n\n";
   }

# ---------------------------------------
# License agreement response.
# ---------------------------------------
   print $mailer "I, ", $value{"REQUESTER"}, " (the Requester) ",
   	$value{"AGREETORESTRICTIONS"},
   	" agree to the $value{\"SYSTEM\"} license restrictions.\n";

# ---------------------------------------
# Text button data.
# ---------------------------------------
   foreach my $variable ( 
         @RequiredParm
       ) {
      if ( $value{$variable} eq "" ) {
         print $mailer "\n" . $PromptText{$variable} .  " no response";
      }
      else {
         print $mailer "\n" . $PromptText{$variable} .  " " . $value{$variable};
      }
   }

   print $mailer "\n\n";
   print $mailer `$create_signature $csparams $value{"SYSTEM"} "$value{"REQUESTER"}" "$value{"EMAIL"}"`;

   if ("$value{\"SYSTEM\"}" eq "SAL") {
     print $mailer "\n\n";
     print $mailer `$create_signature $csparams ICS "$value{"REQUESTER"}" "$value{"EMAIL"}"`;
   }

######################### This will do a complete env dump
## foreach $key ( keys %ENV ) { 
##    print $mailer "$key $ENV{$key}\n";
##}
##########################################################

######################### Calculate script Execution Time
# $finish = (times)[0];
# print $mailer "#############################################\n";
# print $mailer "# EXECUTION TIME \n";
# print $mailer "#############################################\n";
# printf $mailer "Execution took %.2f CPU seconds\n", $finish - $start;
##########################################################

   $mailer->close();
}

# ---------------------------------------
# IllegalChars:
# subroutine to print error message when illegal characters are encountered.
# ---------------------------------------
sub IllegalChars {
   my $variable = $_[0];
   print "Content-type: text/html\n\n";
   print "
<HTML>
<HEAD>
<BODY BGCOLOR=\"#FFFFFF\">
<CENTER>
<BR>
<BR>
<BR>
<H3>
Your $ErrorText{$variable} contains illegal characters or is otherwise not valid.<BR><BR>
Please use the Back button on your browser to return to the form and correct it.<BR>
</H3>
</CENTER>
</BODY>
</HTML>
";

   exit; ### Bail Out Here; bad input!
}
# ---------------------------------------
# writeHTML:
# Read file ${page}.html, fill in any page values that have been defined,
# and write the file to STDOUT.
# ---------------------------------------

sub writeHTML( $ ) {
   my ( $page ) = @_;
   my $name;
   my $linein;

#---------------------------------------------------
# Open input file.
#---------------------------------------------------

   my $filein = "./${page}.template";
   unless (open (IN, "< $filein")) {
      print "\n",
         "*********************************************************\n\n",
         "Temporary problem encountered: ",
         "unable to generate $page code.\n",
         "Click your browser's Reload button or use your browser's\n",
         "Back button to return to the ",
         "preceeding page and try submitting it again.\n\n",
         "If this problem recurs, please contact owre\@csl.sri.com.\n\n",
         "*********************************************************\n\n";
#        "Unable to read $filein.\n  Error message is\n",
#        "  $!\n\n",
      exit 2;
   }

#---------------------------------------------------
# Read file, substitute values, and write to STDOUT.
#---------------------------------------------------

   while (defined ($linein = <IN>)) {
      if ($linein =~ /\?.*\?/ ) {
         foreach $name (keys (%value) ) {
            if (defined $value{$name}) {
               $linein =~ s/\?$name\?/$value{$name}/;
            }
            else {
               $linein =~ s/\?$name\?//;
            }
         }
      }
      print $linein;
   }
   unless (close (IN)) {
      print "\n",
         "*********************************************************\n\n",
         "Unable to close $filein.\n  Error message is\n",
         "  $!\n\n",
         "*********************************************************\n\n";
   }
} # writeHTML
#$ErrorText{"DEBUG"} = join (" ", keys (%value));
#&IllegalChars("DEBUG");
