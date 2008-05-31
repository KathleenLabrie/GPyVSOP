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
ln -sf ../GPyVSOP/gmosLS.py gmosLS
ln -sf ../GPyVSOP/publish.py publish
ln -sf ../GPyVSOP/setvsop.py setvsop
ln -sf ../GPyVSOP/splot.py splot
chmod 0755 gmosLS publish setvsop splot

echo '***'
echo 'export PYTHONPATH=${PYTHONPATH}:'$1'/GPyVSOP'
echo 'export PATH=${PATH}:'$1'/bin'
echo
echo 'setenv PYTHONPATH ${PYTHONPATH}:'$1'/GPyVSOP'
echo 'setenv PATH=${PATH}:'$1'/bin'
echo 'rehash'

