#!/bin/sh
# MIntシステム ワークフロー例題集、ビルドスクリプト for Jenkins

export PATH=/usr/local/bin:$PATH
directories=(./)
pdffilenames=(NIMSのスパコン連携報告書.pdf)
targetdirs=(./)
count=0
logfile="`pwd`/build.log"
# ビルド前削除
if [ -e $logfile ]; then
    rm -f $logfile
fi
# ログファイル作成
touch $logfile

# ビルド
for dir in ${directories[@]}
do
    cd $dir
    make clean
    # make reStracturedText to PDF via tex documents
    echo "-------------------- build latex files ----------" >> $logfile
    echo "make latex" >> $logfile 2>&1
    make latex >> $logfile 2>&1
    echo "-------------------- 1st compile dvi file -----------" >> $logfile
    pushd build/latex
    echo "platex -f --interaction=nonstopmode source_MInt_samples.tex" >> $logfile 2>&1
    platex -f --interaction=nonstopmode source_MInt_samples.tex >> $logfile 2>&1
    echo "-------------------- 2nd compile dvi file -----------" >> $logfile
    echo "platex -f --interaction=nonstopmode source_MInt_samples.tex" >> $logfile 2>&1
    platex -f --interaction=nonstopmode source_MInt_samples.tex >> $logfile 2>&1
    echo "-------------------- convert pdf file -----------" >> $logfile
    echo "dvipdfmx source_MInt_samples.dvi" >> $logfile 2>&1
    dvipdfmx source_MInt_samples.dvi >> $logfile 2>&1
    if [ -e "source_MInt_samples.pdf" ]; then
        # とりあえず成果物確認用ページへコピーする。
        # 本来はちゃんとした公開ページへコピーすること。
        echo "copy source_MInt_samples.pdf to ${pdffilenames[$count]}" >> $logfile
        cp source_MInt_samples.pdf ${pdffilenames[$count]}
        #let count++
    fi
    popd
    echo "-------------------- generate web pages ---------" >> $logfile
    echo "make html" >> $logfile 2>&1
    make html >> $logfile 2>&1
    pushd build
    echo "copy html directory from here to ${targetdirs[$cont]}" >> $logfile
    if [ -e /var/lib/mi-docroot/static/${targetdirs[$count]}/html ]; then >> $logfile
        rm -rf /var/lib/mi-docroot/static/${targetdirs[$count]}/html >> $logfile
    fi >> $logfile
    cp -rp html /var/lib/mi-docroot/static/${targetdirs[$count]}/html >> $logfile
    popd
    let count++
    cd ../
done

# copy to public space for documents
