import boto3,io,zipfile,json,datetime,urllib.request,time
from pathlib import Path
s=boto3.Session(region_name='us-east-1');a=s.client('sts').get_caller_identity()['Account'];assert a=='596189025734'
l=s.client('lambda');g=s.client('apigateway');name='iomt-website-demo';table='iomt-demo-readings';api='rl6z5doxlg'
b=io.BytesIO()
with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:z.write('demo.py','demo.py')
try:l.get_function(FunctionName=name);l.update_function_code(FunctionName=name,ZipFile=b.getvalue());l.get_waiter('function_updated_v2').wait(FunctionName=name)
except l.exceptions.ResourceNotFoundException:
 l.create_function(FunctionName=name,Runtime='python3.12',Role=f'arn:aws:iam::{a}:role/LabRole',Handler='demo.handler',Code={'ZipFile':b.getvalue()},Timeout=10,MemorySize=128,Environment={'Variables':{'TABLE_NAME':table}},Description='Read-only public synthetic demonstration series')
 l.get_waiter('function_active_v2').wait(FunctionName=name)
resources=g.get_resources(restApiId=api)['items'];root=next(r['id'] for r in resources if r['path']=='/')
r=next((r['id'] for r in resources if r['path']=='/demo'),None)
if not r:r=g.create_resource(restApiId=api,parentId=root,pathPart='demo')['id']
arn=f'arn:aws:lambda:us-east-1:{a}:function:{name}'
for m in ['GET','OPTIONS']:
 try:g.put_method(restApiId=api,resourceId=r,httpMethod=m,authorizationType='NONE')
 except g.exceptions.ConflictException:pass
 g.put_integration(restApiId=api,resourceId=r,httpMethod=m,type='AWS_PROXY',integrationHttpMethod='POST',uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{arn}/invocations')
 try:l.add_permission(FunctionName=name,StatementId='website-'+m,Action='lambda:InvokeFunction',Principal='apigateway.amazonaws.com',SourceArn=f'arn:aws:execute-api:us-east-1:{a}:{api}/*/{m}/demo')
 except l.exceptions.ResourceConflictException:pass
db=s.resource('dynamodb').Table(table);now=datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
with db.batch_writer() as w:
 for i,rate in enumerate([73,75,74,77,76,79,78,76,80,79,77,78]):
  w.put_item(Item={'device_id':'website-synthetic-demo','timestamp':(now-datetime.timedelta(minutes=11-i)).isoformat(),'heart_rate':rate,'synthetic':True})
g.create_deployment(restApiId=api,stageName='dev',description='Add read-only synthetic website demo')
endpoint=f'https://{api}.execute-api.us-east-1.amazonaws.com/dev/demo'
for i in range(12):
 try:
  with urllib.request.urlopen(endpoint,timeout=20) as res:
   data=json.load(res);assert data['synthetic'] is True and len(data['readings'])>=12
   assert res.headers.get('Access-Control-Allow-Origin')=='https://lijiabao-2526.github.io'
  break
 except urllib.error.HTTPError:
  if i==11:raise
  time.sleep(5)
print('PUBLIC_SYNTHETIC_READ_PASS',len(data['readings']))
# Query parameters cannot select other users or tables.
with urllib.request.urlopen(endpoint+'?device_id=demo-esp32-01') as res:
 assert json.load(res)['device_id']=='website-synthetic-demo'
print('SUBJECT_OVERRIDE_BLOCKED')
try:urllib.request.urlopen(f'https://{api}.execute-api.us-east-1.amazonaws.com/dev/readings?device_id=demo-esp32-01')
except urllib.error.HTTPError as e:assert e.code==403;print('ORIGINAL_READINGS_STILL_PROTECTED',e.code)
print('WEBSITE_BACKEND_READY',endpoint)
