#!/bin/sh

mkdir -p $1/GPyVSOP
cp gmosLS.py $1/GPyVSOP/
cp gmosLSutil.py $1/GPyVSOP/
cp GPyVSOPutil.py $1/GPyVSOP/
cp publish.py $1/GPyVSOP/
cp setvsop.py $1/GPyVSOP/
cp splot.py $1/GPyVSOP/

mkdir -p $1/bin
cd $1/bin
ln -s ../GPyVSOP/gmosLS.py gmosLS
ln -s ../GPyVSOP/publish.py publish
ln -s ../GPyVSOP/setvsop.py setvsop
ln -s ../GPyVSOP/splot.py splot
chmod 0755 gmosLS publish setvsop splot

echo '***'
echo 'export PYTHONPATH=${PYTHONPATH}:'$1'/GPyVSOP'
echo 'setenv PYTHONPATH ${PYTHONPATH}:'$1'/GPyVSOP'
