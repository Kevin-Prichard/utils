#!/usr/bin/env perl

# usage
# perl cookiejar.pl {{url}} '{{cookie-string}}'


use YAML::Syck qw(Dump);
my $expires = $^T + 86400;
my $path = '/';

my $url = shift;
my $cookies = shift;

printf "--- # %s at %u\n",__FILE__,$^T;
my $domain;
my $p = index($url,'://')+3;
my $l = index($url,'/',$p);
$domain = substr($url,$p,$l-$p);
my $dots = () = $domain =~ /\./g;
printf "dots: %s\n",$dots;
if ($dots > 1) {
   $domain = substr($domain,index($domain,'.'));
} else {
   $domain = '.'.$domain;
}
printf "domain: %s\n",$domain;
printf "url: %s\n",$url;

local *F; open F,'>','cookiejar.txt' or warn $!;
print F <<EOT;
# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.
# domain: $domain
# url: $url

EOT
my @cookies = split'; ',$cookies;
printf "--- %s...\n",Dump(\@cookies);
foreach my $cookie (@cookies) {
   my ($key,$value) = split('=',$cookie);
   if (! $seen{$key}++) {
      # domain access path sec expire cookie value
      printf F "%s\t%s\t%s\t%s\t%s\t%s\t%s\n",$domain,'TRUE',$path,'FALSE',$expires,$key,$value;
   }
 }
close F;
print "info: cookiejar.txt created\n";
printf "cmd: wget --load-cookie-file cookiejar.txt --referer=%s -p %s\n",$domain,$url;
printf "cmd: youtube-dl --cookie cookiejar.txt -referer %s %s\n",$domain,$url;

exit $?;

1; # $Source: /my/perl/scripts/cookiejar.pl $
