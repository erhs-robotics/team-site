#! /bin/bash

str="\`1234567890-qwertyuiop[]\asdfghjkl;\'zxcvbnm,./~\!@#$%^&*()_+QWERTYUIOP\{\}|ASDFGHJKL\:ZXCVBNM<>? 	"
secret="SECRET = \""
for i in {1..100}
do
	rand=$[ $RANDOM % ${#str}-1 ]
	secret+=${str:$rand:1}
done
secret+="\""
echo $secret > src/py/lib/production.py

sed 's/from password/from production/g' src/py/lib/cookie.py > out.txt

rm src/py/lib/cookie.py
mv out.txt src/py/lib/cookie.py

appcfg.py update .

git reset HEAD --hard
