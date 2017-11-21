#!/usr/bin/perl -w

use strict;
use Getopt::Std;

# V2
my $callsign;
my $type;
my $mcip;
my $str;
my %opts;
my $fname;
my $retcode;
my $description;
#my $domain;
my $sm;
my $token;
my $sd_only_1pro = 0;

getopts('hi:t:sd:', \%opts);

usage() if ( ! %opts );
#usage() if ( !$opts{i} || !$opts{d} );
usage() if ( !$opts{i} );
usage() if ( $opts{h} );

$fname  = $opts{i};
#$domain = $opts{d};

if ( $opts{s} ) {
        $sd_only_1pro = 1;
}

#$sm = 'service-mgr.' . $domain;
$sm = '100.64.79.111';
$token = gettoken($sm);

$fname = create_input_file($fname);

open(ELOG,">elog.txt") or die "Can't open elog.txt\n";
open(FILE,$fname) or die "Can't open $fname\n";
open(CS,">callsigns") or die "Can't open callsigns\n";

# Build streaming Profiles if they don't exist
my @profiles = (450,600,1000,1500,2200,4000,300,625,925,1200);

foreach (@profiles) {

        my $sp_exist = checkSP($_,$token,$sm);

                if ( $sp_exist != 200 ) {
                        $sp_exist = buildSP($_,$token,$sm);

                        if ( $sp_exist == 200 ) {
                                 #print "Streaming Profile $_ built\n";
                         } else {
                                 print ELOG "Streaming Profile $_ not built\n";
                         }
                }
}



while(<FILE>) {
        chomp($_);
        ($description,$callsign,$type,$mcip) = split(/,/, $_);

        $type = uc($type);

    print CS "$callsign\n";

    if ( $sd_only_1pro == 0 ) {
            if ( $type eq 'HD' ) { 
            #if ( $type =~ /4004/ ) { 
                buildHDJsonFile($callsign,$mcip,$description);
            } else {
                buildSDJsonFile($callsign,$mcip,$description);
            }
    } else {
            buildSDJsonFile_1pro($callsign,$mcip,$description);
    }

    # if channel exists, skip
    $retcode = channel_exists($callsign,$token,$sm);

    if ( $retcode != 200 ) {
            ## If channel does not exist, add channel to V2P ##
            $retcode = addchannel($callsign,$token,$sm);


                if ( $retcode != 200 ) {
                        print ELOG "CHANNEL CREATION FAILED: $_\n";
                } 
    
    } else {
        print "Channel $callsign already exists in the system..Skipping...\n";
    }


        ## Delete JSON build File
        unlink("build");

}

close FILE;
close ELOG;
close CS;

sub addchannel {
# Token following the word Bearer comes from the PAM in /etc/opt/cisco/mos/public/token.json
my $cs  = shift;
my $t_token = shift;
my $sm = shift;

my $res = `curl -w "%{http_code}" -o /dev/null -k -v -H "Authorization: Bearer $t_token"  https://$sm:8443/api/platform/do/v2/channelsources/$cs -H Content-Type:application/json -X POST -d \@build > /dev/null 2>&1`;
#$res = `curl -w "%{http_code}"  -k -v -H "Authorization: Bearer $t_token"  https://$sm:8443/api/platform/do/v2/channelsources/$cs -H Content-Type:application/json -X POST -d \@build `;
$res = `curl -w "%{http_code}" -o /dev/null -k -v -H "Authorization: Bearer $t_token"  https://$sm:8443/api/platform/do/v2/channelsources/$cs -H Content-Type:application/json -X PUT -d \@build 2>/dev/null`;
#$res = `curl -w "%{http_code}" -k -v -H "Authorization: Bearer $t_token"  https://$sm:8443/api/platform/do/v2/channelsources/$cs -H Content-Type:application/json -X PUT -d \@build `;

return $res;

}

sub channel_exists {

my $cs  = shift;
my $t_token = shift;
my $sm = shift;


my $res = `curl -w "%{http_code}" -o /dev/null -H "Authorization: Bearer $t_token" -ks https://$sm:8443/api/platform/do/v2/channelsources/$cs `;

return $res;

}


sub buildHDJsonFile {
my $cs = shift;
my $mc = shift;
my $desc = shift;

$str =  <<EOF;
{
  "id": "smtenant_0.smchannelsource.$cs",
  "name": "$cs",
  "type": "channelsources",
  "externalId": "/v2/channelsources/$cs",
  "properties": {
    "channelId": "$cs",
    "description": "$desc",
    "streamType": "ATS",
    "streams": [
      {
        "profileRef": "smtenant_0.smstreamprofile.450k",
        "sources": [
          {
            "sourceUrl": "udp://$mc:4001",
            "sourceIpAddr": ""
          }
        ]
      },
      {
        "profileRef": "smtenant_0.smstreamprofile.600k",
        "sources": [
          {
            "sourceUrl": "udp://$mc:4002",
            "sourceIpAddr": ""
          }
        ]
      },
      {
        "profileRef": "smtenant_0.smstreamprofile.1000k",
        "sources": [
          {
            "sourceUrl": "udp://$mc:4003",
            "sourceIpAddr": ""
          }
        ]
      },
      {
        "profileRef": "smtenant_0.smstreamprofile.1500k",
        "sources": [
          {
            "sourceUrl": "udp://$mc:4004",
            "sourceIpAddr": ""
          }
        ]
      },
      {
        "profileRef": "smtenant_0.smstreamprofile.2200k",
        "sources": [
          {
            "sourceUrl": "udp://$mc:4005",
            "sourceIpAddr": ""
          }
        ]
      },
      {
        "profileRef": "smtenant_0.smstreamprofile.4000k",
        "sources": [
          {
            "sourceUrl": "udp://$mc:4006",
            "sourceIpAddr": ""
          }
        ]
      }
    ]
  }
}
EOF

open(BUILD,">build");
print BUILD "$str\n";
close BUILD;

}

sub buildSDJsonFile {
my $cs = shift;
my $mc = shift;
my $desc = shift;

$str =  <<EOF;
{
  "id": "smtenant_0.smchannelsource.$cs",
  "name": "$cs",
  "type": "channelsources",
  "externalId": "/v2/channelsources/$cs",
  "properties": {
    "channelId": "$cs",
    "description": "$desc",
    "streamType": "ATS",
    "streams": [
      {
        "profileRef": "smtenant_0.smstreamprofile.300k",
        "sources": [
          {
            "sourceUrl": "udp://$mc:4001",
            "sourceIpAddr": ""
          }
        ]
      },
      {
        "profileRef": "smtenant_0.smstreamprofile.625k",
        "sources": [
          {
            "sourceUrl": "udp://$mc:4002",
            "sourceIpAddr": ""
          }
        ]
      },
      {
        "profileRef": "smtenant_0.smstreamprofile.925k",
        "sources": [
          {
            "sourceUrl": "udp://$mc:4003",
            "sourceIpAddr": ""
          }
        ]
      },
      {
        "profileRef": "smtenant_0.smstreamprofile.1200k",
        "sources": [
          {
            "sourceUrl": "udp://$mc:4004",
            "sourceIpAddr": ""
          }
        ]
      }
    ]
  }
}
EOF

open(BUILD,">build");
print BUILD "$str\n";
close BUILD;

}

sub buildSDJsonFile_1pro {
my $cs = shift;
my $mc = shift;
my $desc = shift;

$str =  <<EOF;
{
  "id": "smtenant_0.smchannelsource.$cs",
  "name": "$cs",
  "type": "channelsources",
  "externalId": "/v2/channelsources/$cs",
  "properties": {
    "channelId": "$cs",
    "description": "$desc",
    "streamType": "ATS",
    "streams": [
      {
        "profileRef": "smtenant_0.smstreamprofile.300k",
        "sources": [
          {
            "sourceUrl": "udp://$mc:4001",
            "sourceIpAddr": ""
          }
        ]
      }
    ]
  }
}
EOF

open(BUILD,">build");
print BUILD "$str\n";
close BUILD;

}

sub usage {

print <<EOF;

The following parameters are required: 

i:      Name of Excel input file ( ex. $0 -i file.csv )
s:      SD Build only (1 SD Profile, UDP 4001 )
d:      Domain name (ex. mos.hcvlny.cv.net)
h:      Help message


EOF

exit;
}

sub create_input_file {

my $fname = shift;
my $filename = 'input_file_parsed.txt';
my $haserrors = 0;
my %cs_list;
my $desc;
my $cs;
my $sip;
my $type;
my $mcip;
my $line;
my $rownum = 0;

open(FILEN,">$filename") or die "Can't open $filename\n";
open(F,$fname);

        while($line = <F>) {
                $rownum++;
                chomp($line);
                ($desc,$cs,$mcip,$type,$sip) = split(/,/, $line);

                print FILEN "$desc,$cs,$sip,$type,$mcip\n";
                
                if ( $cs eq "" ) {
                    print "No callsign defined on line $rownum\n";
                }
                # Error checking.  Must check for unique callsigns and ensure other fields are valid
                #

                    if ( exists $cs_list{$cs} ) {
                            print "$cs is NOT Unique, rows $rownum,$cs_list{$cs} \n";
                    $haserrors = 1;
                    } else {
                    if ( $cs ne "" ) {
                                $cs_list{$cs} = $rownum;
                    }
                    }

                if ( $mcip !~ /\d+\.\d+\.\d+\.\d+/ ) {
                            print "Invalid Multicast IP $mcip, row $rownum.  Please correct\n";
                    $haserrors = 1;
                    }
                if ( $sip !~ /\d+\.\d+\.\d+\.\d+/ ) {
                    $haserrors = 1;
                            print "Invalid Source IP $sip, row $rownum.  Please correct\n";
                    }

                # Check for invalid characters
                    if ( $cs =~ /_|\s+|\+|\!|\&/ ) {
                    $haserrors = 1;
                    print "Invalid character(s) found in callsign $cs, row $rownum.  Please correct\n";
                }


        }
close FILEN;

if ( $haserrors == 1 ) {
    print "Errors found in file.  Correct the errors and re-execute. NO CHANGES MADE..Exiting..\n";
    exit(2);
} else {
   return $filename;
}

}

sub gettoken {
$token = `curl -X POST -ks https://10.8.3.25:8443/api/platform/login -d '{"username":"admin","password":"default"}' -H 'Content-Type:application/json'`;
$token =~ s/{"token":"//g;
$token =~ s/"}$//g;
return $token;
}

sub buildSP {
my $str;
my $rate;
my $name;
my $br = shift;
my $t_token = shift;
my $sm = shift;
my $res;

$rate = $br * 1000;
$name = $br . 'k';
$str .=  <<EOF;
{
 "name" : "$name",
 "id" : "smtenant_0.smstreamprofile.$name",
 "type" : "streamprofiles",
 "externalId" : "/v2/streamprofiles/$name",
 "properties" : {
   "encodingType" : "H.264",
   "bitrate" : "$rate"
 }
}
EOF

chomp($str);

open(PROF,">prof");
 print PROF "$str\n";
close PROF;

$res = `curl -k -w "%{http_code}" -o /dev/null -v -H "Authorization: Bearer $t_token"  https://$sm:8443/api/platform/do/v2/streamprofiles/$name -X POST -H Content-Type:application/json -d \@prof 2>/dev/null`;

 #unlink("prof");
 return $res;
}

sub checkSP {

my $br = shift;
my $t_token = shift;
my $sm = shift;

$br .= 'k';

my $res = `curl -k -w "%{http_code}" -o /dev/null -v -H "Authorization: Bearer $t_token"  https://$sm:8443/api/platform/do/v2/streamprofiles/$br -X GET  2> /dev/null`;

return $res;

}
