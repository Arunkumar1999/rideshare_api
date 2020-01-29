import sqlite3
from flask import Flask, render_template,jsonify,request,abort,Response
import requests
import json
import csv
app=Flask(__name__)
cursor = sqlite3.connect("rideshare.db")
#cursor = conn.cursor()
#cursor.execute("create database if not exists rideshare;")
#cursor.execute("create database if not exists rideshare")
#cursor.execute("(select * from INFORMATION_SCHEMA.TABLES where table_name='specialtopic') ;")





cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
          name varchar(20) primary key,
  		  pass varchar(20)
        );
    """)

cursor.execute("""
        CREATE TABLE IF NOT EXISTS rideusers(
         id int not null,
  		 name varchar(20),
		foreign key (name) references users(name) on delete cascade,
		foreign key (id) references rides(rideid) on delete cascade,
		primary key(id,name)
        );
    """)

cursor.execute("""
    CREATE TABLE IF NOT EXISTS place(
      id int primary key,
	  name varchar(20)
    );
""")
with open('AreaNameEnum.csv') as File:  
	reader = csv.reader(File)
	#print(reader)

	i=0
	for row in reader:
		#print(row[0],row[1])
		if(i):
			#print(row)
			try:
				d=[row[0],row[1]]
				#res=requests.post("http://127.0.0.1:5000/api/v1/db/write",json={"insert":d,"column":["id","name"],"table":"place","indicate":"0"})		
				sql="insert into place values (?,?)"
				#sql="insert into users (name,pass) values ('dsfs','sdf')"
				#print("dfs",table,column,s,val,sql)
				#print(sql,type((table.encode("utf8"))),r)
				cursor.execute(sql,d)
				#cursor.execute(sql)
			except:
				continue	
		i=1		
	cursor.commit()

cursor.execute("""
        CREATE TABLE IF NOT EXISTS rides(
          rideid integer  primary key AUTOINCREMENT,
          name varchar(20) not null ,
  		  timest time not null,
  		  source varchar(30) not null,
  		  desti varchar(30) not null,
  		  foreign key (name) references users(name) on delete cascade, 
  		  foreign key (source) references place(id) on delete cascade,
  		  foreign key (desti) references place(id) on delete cascade
        );
    """)

cursor.commit()

def fun(passw):
	if(len(passw)!=40):
		return 0
	for i in passw:
		if(not i.isdigit() and not (i.isalpha() and ord('a')<=ord(i) and ord('f')>=ord(i)) ):
			return 0
	return 1


@app.route("/api/v1/db/read",methods=["POST"])
def read_database():
	cursor = sqlite3.connect("rideshare.db")
	resp_dict={}
	val=request.get_json()["insert"]
	table=request.get_json()["table"].encode("utf8")
	column=request.get_json()["column"]
	r=""
	s=""
	e=len(column)-1
	for i in range(e):
		r+=column[i].encode("utf8")+","
		s+="?,"
	r+=column[e].encode("utf8")
	s+="?"
	for i in range(len(val)):
		val[i]=val[i].encode("utf8")

	#try:
	sql="select "+r+" from "+table+" where "+column[0]+"=(?)"
	print(sql)
	#et=cursor.execute(sql,(delete,))
	resp=cursor.execute(sql,(val[0],))
	#print(val[0])
	print(resp)
	resp_check=resp.fetchall()
	#print(resp_check)
	if(len(resp_check)== 0):
		resp_dict["response"]=0
		return json.dumps(resp_dict)
	else:
		
		print(resp_check)
		print(list(resp_check[0]))
		print(len(resp_check),"count of all rows")
		resp_dict["count"]=len(resp_check)
		for i in range(len(resp_check)):
			#print("inside for loop")
			for j in range(len(column)):
				resp_dict[column[j]]=list(resp_check[i])[j]
		print(resp_dict,"hii i am dict")
		print("user does exists from read_Db")
		resp_dict["response"]=1
		return json.dumps(resp_dict)

@app.route("/api/v1/db/write",methods=["POST"])
def to_database():
	
	indicate=request.get_json()["indicate"]
	#print(indicate.encode("utf8")=='0')
	#return jsonify(2)
	cursor = sqlite3.connect("rideshare.db")
	cursor.execute("PRAGMA FOREIGN_KEYS=on")
	cursor.commit()
	if(indicate.encode("utf8")=='0'):
		val=request.get_json()["insert"]
		table=request.get_json()["table"].encode("utf8")
		column=request.get_json()["column"]
		r=""
		s=""
		e=len(column)-1
		for i in range(e):
			r+=column[i].encode("utf8")+","
			s+="?,"
		r+=column[e].encode("utf8")
		s+="?"
		for i in range(len(val)):
			val[i]=val[i].encode("utf8")
			#rt=val[1].encode("utf8")

				
		

		try:

			sql="insert into "+table+" ("+r+")"+" values ("+s+")"
			#sql="insert into users (name,pass) values ('dsfs','sdf')"
			#print("dfs",table,column,s,val,sql)
			#print(sql,type((table.encode("utf8"))),r)
			cursor.execute(sql,val)
			#cursor.execute(sql)


			cursor.commit()
			sql="select * from "+table
			et=cursor.execute(sql)
			rows = et.fetchall()
			# for row in rows:
			# 	print(row,"qer")
			sql="select * from users"
			et=cursor.execute(sql)
			rows = et.fetchall()
			# for row in rows:
			# 	print(row,"q")			
		except:
			sql="select * from "+table
			et=cursor.execute(sql)
			rows = et.fetchall()
 			for row in rows:
				print(row,"we")
			#print("dasd")
			return jsonify(0)
		return jsonify(1)
	elif(indicate.encode("utf8")=='1'):
		table=request.get_json()["table"].encode("utf8")
		delete=request.get_json()["delete"].encode("utf8")
		column=request.get_json()["column"].encode("utf8")
		try:
			sql="select * from "+table+" WHERE "+column+"=(?)"
			et=cursor.execute(sql,(delete,))
			#print(et.fetchone())
			if(not et.fetchone()):
				return jsonify(0)
			
			sql = "DELETE from "+table+" WHERE "+column+"=(?)"
			print(sql)
			c1 = cursor.cursor()
			et=cursor.execute(sql,(delete,))
			print(et.fetchall())
			cursor.commit()
			#cursor.close()
		except:
			#print("dssf")
			return jsonify(0)
		return jsonify(1)



@app.route("/api/v1/users",methods=["PUT"])
def add():
	#access book name sent as JSON object 
	#in POST request body
	name=request.get_json()["username"]
	passw=request.get_json()["password"]
	#if(name not in d ):
		#if(fun(passw)):
	d=[name,passw]
	#d[]=
	if(fun(passw)==0):
		abort(400,"password is not correct")
		#return jsonify(2) #password validation
	res=requests.post("http://127.0.0.1:5000/api/v1/db/write",json={"insert":d,"column":["name","pass"],"table":"users","indicate":"0"})	
	#print(res=="a",res=="b",res.json()==1,res.json()==0)
	#return "dsf"
	
	if(res.json()==2):
			abort(400,"password is not correct")	
	elif(res.json()==0):
		abort(400,"user already exists")
	#abort (200,"success" )
	#return json.dumps({'success':"saved"}), 200, {'ContentType':'application/json'}
	return Response("success",status=201,mimetype='application/json')
#cursor.execute("(select * from INFORMATION_SCHEMA.TABLES where table_name='specialtopic') ;")
#result = cursor.fetchone()
rides=[]
rides_id=0
sour={}
des={}

@app.route("/api/v1/rides",methods=["POST"])
def insert_rider():
	#access book name sent as JSON object 
	#in POST request body
	global rides_id
	name=request.get_json()["created_by"]
	passw=request.get_json()["timestamp"]
	source=request.get_json()["source"]
	destination=request.get_json()["destination"]
	d=[name,passw,source,destination]
	#print(dsd)
	read_res=requests.post("http://127.0.0.1:5000/api/v1/db/read",json={"insert":d,"column":["name","pass"],"table":"users"})
	if(read_res.json().get("response")==0):
		abort(400,"user name doesn't exists")

	res=requests.post("http://127.0.0.1:5000/api/v1/db/write",json={"insert":d,"column":["name","timest","source","desti"],"table":"rides","indicate":"0"})
	#if(name in d ):
		# rides.append({"rideId":rides_id,"username":name,"timestamp":passw,"source":source.keys()[0],"destination":destination.keys()[0]})
		# sour.update(source)
		# des.update(destination)
		# rides_id+=1
		# print(sour,des,rides,rides_id)
	#else:
	#	abort(400,"user not found")
	#return (201,"success" )
	#return json.dumps({'success':"rider has been updated"}), 200, {'ContentType':'application/json'}
	if(res.json()==2):
			abort(400,"password is not correct")	
	elif(res.json()==0):
		abort(400,"user already exists")
	#abort (200,"success" )
	#return json.dumps({'success':"saved"}), 200, {'ContentType':'application/json'}
	return Response("success",status=201,mimetype='application/json')
#cursor.execute("(select * from INFORMATION_SCHEMA.TABLES where table_name='specialtopic') ;")
#result = cursor.fetchone()
#print(d)


#REMOVE
@app.route("/api/v1/users/<name>",methods=["DELETE"])
def remove(name):
	#access book name sent as JSON object 
	#in POST request body
	#name=request.get_json()["username"]
	#passw=request.get_json()["password"]f
	#if(name in d ):
	#	del d[name]	
	res=requests.post("http://127.0.0.1:5000/api/v1/db/write",json={"table":"users","delete":name,"column":"name","indicate":"1"})
	# res=requests.post("http://127.0.0.1:5000/api/v1/db/write",json={"table":"rides","delete":name,"column":"name","indicate":"1"})
	if(res.json()==0):
		abort(400,"user does not  exists")
	elif(res.json()==1):
		return json.dumps({'success':"user has been deleted successfully"}), 200, {'ContentType':'application/json'}

@app.route("/api/v1/rides/<rideId>",methods=["DELETE"])
def delete_rideId(rideId):
	#access book name sent as JSON object 
	#in POST request body
	#name=request.get_json()["username"]
	#passw=request.get_json()["password"]f
	#if(name in d ):
	#	del d[name]	
	res=requests.post("http://127.0.0.1:5000/api/v1/db/write",json={"table":"rides","delete":rideId,"column":"rideid","indicate":"1"})
	if(res.json()==0):
		abort(400,"rideId does not  exists")
	elif(res.json()==1):
		return json.dumps({'success':"deleted successfully"}), 200, {'ContentType':'application/json'}

@app.route("/api/v1/rides/<rideId>",methods=["POST"])
def join_ride(rideId):
	name=request.get_json()["username"]
	d=[name,rideId]
	read_res=requests.post("http://127.0.0.1:5000/api/v1/db/read",json={"insert":d,"column":["name","pass"],"table":"users"})
	if(read_res.json().get("response")==0):
		abort(400,"user doesn't exists")
	d=[rideId,name]
	rideid_check=requests.post("http://127.0.0.1:5000/api/v1/db/read",json={"insert":d,"column":["rideid","name","source","desti"],"table":"rides"})
	if(rideid_check.json().get("response")==0):
		abort(400,"ride id doesn't exists")
	
	res=requests.post("http://127.0.0.1:5000/api/v1/db/write",json={"insert":d,"column":["id","name"],"table":"rideusers","indicate":"0"})
	if(res.json()==0):
		abort(400,"rideId does not  exists")
	elif(res.json()==1):
		return json.dumps({'success':"joined successfully"}), 200, {'ContentType':'application/json'}

@app.route("/api/v1/rides/<rideId>",methods=["GET"])
def ride_details(rideId):
	#access book name sent as JSON object 
	#in POST request body
	#name=request.get_json()["username"]
	#passw=request.get_json()["password"]f
	#if(name in d ):
	#	del d[name]	
	d=[rideId]
	rideid_check=requests.post("http://127.0.0.1:5000/api/v1/db/read",json={"insert":d,"column":["rideid","name","source","desti","timest"],"table":"rides"})
	if(rideid_check.json().get("response")==0):
		abort(400,"rideId does not  exists")
	elif(rideid_check.json().get("response")==1):
		return json.dumps({"rideId":rideid_check.json().get("rideid"),"created_by":rideid_check.json().get("name"),
							"users":rideid_check.json().get("name"),
							"timestamp":rideid_check.json().get("timest")}), 200, {'ContentType':'application/json'}

app.debug=True
app.run()


'''
@app.route('/api/v1/resources/books', methods=['GET'])
def api_filter():
    query_parameters = request.args

    id = query_parameters.get('id')
    published = query_parameters.get('published')
    author = query_parameters.get('author')

    query = "SELECT * FROM books WHERE"
    to_filter = []

    if id:
        query += ' id=? AND'
        to_filter.append(id)
    if published:
        query += ' published=? AND'
        to_filter.append(published)
    if author:
        query += ' author=? AND'
        to_filter.append(author)
    if not (id or published or author):
        return page_not_found(404)

    query = query[:-4] + ';'

    conn = sqlite3.connect('books.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)

app.run()
'''
'''
#input
{
	"username":"rakesh",
	"password":"1234567892015478ac45123654789ba123456012"
}


#2
{
	"created_by" : "rakesh",

	"timestamp" : "22-05-0999:12-00-01",
	
	"source" : {"21":"bangalore"},

	"destination" : {"32":"hubli"}
}
'''