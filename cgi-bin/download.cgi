#!/usr/bin/perl -w

use CGI ':standard';
use CGI::Carp qw(fatalsToBrowser);
use File::Basename;

my $request_method = $ENV{'REQUEST_METHOD'};
my $request = $ENV{'QUERY_STRING'};
my $file=param('file');
my $accept=param('accept');
my $reject=param('reject');

if ($accept eq 'I accept') {

    # Get list of tar files in the binaries directory
    opendir(DIR, "binaries") or die "Requested tarfile $file not found\n\n";
    my @list=readdir(DIR);
    closedir(DIR);

    # Check that the requested file is in the list.
    undef $found;
    foreach $f (@list) {
	$found = "yes", last if ($f eq $file);
    }

    # Error
    unless (defined $found) {
	die "Requested tarfile $file not found\n\n";
    }

    #
    open(TARFILE, "<binaries/$file") or die "Requested tarfile $file not found\n\n";
    @file_holder = <TARFILE>;
    close(TARFILE);

    print "Content-type:application/x-download\n";
    print "Content-disposition:attachment;filename=$file\n\n";
    print @file_holder
    

} else {
    #
    # Rejection page.
    #
    print "Content-Type: text/html\n\n";

    open(REJECT,"reject-license.template") or die "File not found\n\n";

    while (<REJECT>) {
	print;
    }

    close(REJECT);
}
