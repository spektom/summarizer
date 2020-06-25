#!/bin/bash -e

for package in stopwords punkt wordnet
do
  python -c "import nltk; nltk.download('${package}', download_dir='.data');"
done

if [ ! -f .data/stanford-ner.jar ]
then
  cd .data
  wget -c https://nlp.stanford.edu/software/stanford-ner-4.0.0.zip
  unzip stanford-ner-4.0.0.zip
  mv stanford-ner-4.0.0/classifiers/english.all.3class.distsim.crf.ser.gz .
  mv stanford-ner-4.0.0/stanford-ner.jar .
  rm -rf stanford-ner-4.0.0*
fi
