#!/usr/bin/env bash

find * -iname '*10.jpg' -size +10k |perl -ane '
BEGIN{
    ($Q, $S, $L, $G) = (chr(34), chr(47), chr(60), chr(62));
    print "<!DOCTYPE HTML><html><head>
    <style>a{padding:2.5px}</style>
    <script type=\"text/javascript\">
    // debugger;
    window.imageIters = false;
    let a;
    async function sleep(milliseconds) {
        return new Promise(resolve => setTimeout(resolve, milliseconds));
    }
    async function imageIter(id,url,num,pad) {
        // debugger;
        if (window.imageIters === true) return;
        console.log(\"Started ${id}\");
        window.imageIters = true;
        const img = document.getElementById(`\${id}_img`),
              origUrl=img.src;
        async function repeater(ptr) {
            // debugger;
            while (ptr++ < num && window.imageIters === true) {
                img.src=url.replace(\"__f__\", pad < 0 ? ptr : (\"0000\" + ptr).slice(-pad));
                img.onerror=() => {console.log(`Error on \${img.src}`); ptr = ptr >= num ? 0 : ptr;}
                console.log(img.src);
                await sleep(200);
            }
            img.src = origUrl;
            window.imageIters = false;
        };
        await repeater(0);
        window.imageIters = false;
        img.src = origUrl;
    };
    </script></head>
    <body>";
}

chop;
my($p,$f)=split/\//;
$p=~s|#|%23|;
$u="${p}/${f}";
($digits)=$f=~m/(\d+)/;
$pad_digits = substr($digits, 0, 1) == "0" ? length $digits : -1;
print STDERR "digits = \"${digits}\"; pad_digits = \"${pad_digits}\"\n";
$ff=$f;
$ff=~s/\d+/__f__/;
$uf="${p}/${ff}";
#print STDERR "uf = \"${uf}\"\n";
$id=$p;
$id=~s/[^a-z0-9_\-]+/_/gi;
print "<a id=\"${id}\" href=\"${p}\"><img id=\"${id}_img\" src=\"${u}\" width=\"200\" /></a>\n\n";
push @a, "a=document.getElementById(\"${id}\");
a.onmouseenter=() => imageIter(\"${id}\",\"${uf}\",50,${pad_digits});
a.onmouseleave=() => {console.log(\"Left ${id}\"); window.imageIters = false;}
";

END {
    $"="\n";
    print "
<script type=\"text/javascript\">
@a
</script></body></html>
";
}
' > index.html
