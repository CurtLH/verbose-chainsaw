# verbose-chainsaw

Source: https://docs.aws.amazon.com/lambda/latest/dg/python-package.html#python-package-dependencies

## How to upload new version
```
pip install --target ./package -r requirements.txt 
cd package
zip -r9 ${OLDPWD}/function.zip .
cd $OLDPWD
zip -g function.zip lambda_function.py
aws lambda update-function-code --function-name myFunction --zip-file fileb://function.zip
```
