#!/bin/bash

set -e

url='http://opus.nlpl.eu/download.php?f=OpenSubtitles2018/en-fr.txt.zip'
scripts=scripts

echo "| Downloading and unzipping corpus..."

# download OpenSubtitles 2018 EN-FR and unzip
if [ `ls OpenSubtitles.* 2> /dev/null | wc -l` == 3 ]; then
    echo "| - OpenSubtitles seems to be downloaded and unzipped already. To repeat download, remove one of  ['OpenSubtitles.en-fr.ids', 'OpenSubtitles.en-fr.en', 'OpenSubtitles.en-fr.fr']."
else
    wget $url -O source.en-fr.zip
    unzip -o source.en-fr.zip
fi

echo "| Extracting documents from XML files..."

# extract documents
if [ ! -d documents ]; then
    mkdir documents
    perl $scripts/opusXML2docs.pl --ids OpenSubtitles.en-fr.ids --l1 en --l2 fr --outdir documents --source OpenSubtitles.en-fr.en --target OpenSubtitles.en-fr.fr
else
    echo "| - Documents seem to be extracted already. To repeat extraction, remove the folder 'documents'."
fi

echo "| Organize into folders by year and clean up..."

# organize into folders
if [ ! -d documents/1916 ]; then
    for file in documents/*; do
        mkdir -p -- "${file%%_*}"
        mv -- "$file" "${file%%_*}"
    done
else
    echo "| - Documents seem to be organized by year already. To repeat, remove all subfolders documents/*"
fi

# remove a stray document pair
rm -rf documents/1191

# remove source files - comment out if you would like to keep them
rm -f source.en-fr.zip
#rm -f OpenSubtitles.en-fr.{fr,en,ids}
#rm -f doc.order.en-fr.txt
rm -f README
