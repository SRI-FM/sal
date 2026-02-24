#!/usr/bin/perl -w

$title = "SAL (with Yices) License";
if ("$ENV{SERVER_NAME}" eq "sal.csl.sri.com") {
    $base = "http://sal.csl.sri.com/";
} else {
    $base = "../data/";
}
$prelude_shtml = "../data/sal-prelude.shtml";
$postlude_shtml = "../data/navbar.shtml";

use CGI ':standard';
use CGI::Carp qw(fatalsToBrowser);
use File::Basename;
require "ssi_parse.pl";

my $file; 
my @fileholder;

# Get the basename, so nobody can try to use, e.g., ../../../etc/passwd
$file = basename(param('file'));
$accept = param('accept');

if ($accept eq 'I accept') {

    if ($file eq '') { 
	print "Content-type: text/html\n\n"; 
	print "You must specify a file to download."; 
    } else {
	
	open(DLFILE, "<../data/download/$file") || Error('open', 'file'); 
	@fileholder = <DLFILE>; 
	close (DLFILE) || Error ('close', 'file'); 
	
	print "Content-Type:application/x-download\n"; 
	print "Content-Disposition:attachment;filename=$file\n\n";
	print @fileholder;
    }
} else {
    #
    # Rejection page.
    #
    print "Content-Type: text/html\n\n";

    ssi_parse_and_output("sed -e 's!____BASEURL!$base!g' reject-license.template |",
			 'fh00');
}


sub Error {
      print "Content-type: text/html\n\n";
	print "The server can't $_[0] the $_[1]: $! \n";
	exit;
}
