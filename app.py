from flask import Flask,request,redirect,session,render_template_string
import sqlite3,os,pandas as pd,numpy as np
from sklearn.ensemble import IsolationForest
app=Flask(__name__);app.secret_key=os.getenv('SECRET_KEY','bizbuddy-secret-2026');DB='bizbuddy.db'
def db():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;return c
def init():
 c=db();c.executescript('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT UNIQUE,password TEXT,mode TEXT DEFAULT "professional");CREATE TABLE IF NOT EXISTS sales(id INTEGER PRIMARY KEY,date TEXT,product TEXT,quantity REAL,price REAL,revenue REAL);CREATE TABLE IF NOT EXISTS expenses(id INTEGER PRIMARY KEY,date TEXT,category TEXT,amount REAL);CREATE TABLE IF NOT EXISTS inventory(id INTEGER PRIMARY KEY,product TEXT,stock REAL,reorder_level REAL);''');c.execute("INSERT OR IGNORE INTO users(username,password) VALUES('admin','BizBuddy@2026')");c.commit();c.close()
def sales():
 c=db();d=pd.read_sql_query('SELECT * FROM sales',c);c.close();
 if not d.empty:d.date=pd.to_datetime(d.date);d.revenue=pd.to_numeric(d.revenue,errors='coerce').fillna(0)
 return d
def exp():
 c=db();d=pd.read_sql_query('SELECT * FROM expenses',c);c.close();return d
def inv():
 c=db();d=pd.read_sql_query('SELECT * FROM inventory',c);c.close();return d
def analysis():
 s,e,i=sales(),exp(),inv();r=float(s.revenue.sum()) if not s.empty else 0;x=float(e.amount.sum()) if not e.empty else 0;low=int((i.stock<=i.reorder_level).sum()) if not i.empty else 0;best=s.groupby('product').revenue.sum().idxmax() if not s.empty else 'No data';return r,x,r-x,low,best
def forecast():
 s=sales()
 if s.empty:return 0
 d=s.groupby('date').revenue.sum().sort_index().tail(7)
 if len(d)<3:return float(d.mean())
 m,b=np.polyfit(np.arange(len(d)),d.values,1);return max(0,float(m*len(d)+b))
def anomalies():
 s=sales()
 if len(s)<5:return []
 d=s.groupby('date').revenue.sum().reset_index()
 if len(d)<5:return []
 d['p']=IsolationForest(contamination='auto',random_state=42).fit_predict(d[['revenue']]);return d[d.p==-1].to_dict('records')
def agent():
 r,e,p,low,best=analysis();a=anomalies();rec=[];alerts=[]
 if low:rec.append('Replenish low-stock products before they affect sales.');alerts.append(('Low Inventory Detected',f'{low} product(s) are at or below reorder level.','HIGH','Review inventory and place a restocking order.'))
 if a:rec.append('Investigate unusual sales activity and related dates/products.');alerts.append(('Sales Anomaly Detected',f'{len(a)} unusual sales period(s) detected.','HIGH','Investigate the unusual sales pattern and prepare stock accordingly.'))
 if p<0:rec.append('Review major expenses because expenses exceed revenue.');alerts.append(('Negative Profit','Recorded expenses are higher than revenue.','CRITICAL','Review pricing and unnecessary expenses.'))
 if not rec:rec=['Business activity looks stable. Continue monitoring sales, expenses and inventory.']
 return rec,alerts,forecast(),a
CSS='''*{box-sizing:border-box}body{margin:0;font-family:Arial;background:#f4f7fb;color:#172033}nav{background:#111827;color:white;padding:18px 30px;display:flex;justify-content:space-between}nav a{color:white;margin-left:18px;text-decoration:none}.wrap{max-width:1200px;margin:30px auto;padding:0 20px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:18px}.card,.panel{background:white;border-radius:15px;padding:22px;box-shadow:0 4px 15px #0001}.panel{margin-top:22px}.value{font-size:28px;font-weight:bold;margin-top:8px}.muted{color:#667085}.alert{border-left:5px solid #ef4444;padding:15px;margin:12px 0;background:#fff5f5;border-radius:8px}input,select,button{width:100%;padding:12px;margin:7px 0 14px;border-radius:8px}button{background:#2563eb;color:white;border:0;cursor:pointer}.login{max-width:400px;margin:100px auto}.badge{padding:5px 9px;background:#fee2e2;color:#991b1b;border-radius:15px}'''
PAGE='''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>BizBuddy AI</title><style>'''+CSS+'''</style></head><body><nav><b>🤖 BizBuddy AI</b>{%if session.get('user')%}<span><a href="/dashboard">Dashboard</a><a href="/upload">Upload</a><a href="/alerts">Alerts</a><a href="/mode">Mode</a><a href="/logout">Logout</a></span>{%endif%}</nav><main class="wrap">{{content|safe}}</main></body></html>'''
def page(x):return render_template_string(PAGE,content=x)
@app.route('/',methods=['GET','POST'])
def login():
 if session.get('user'):return redirect('/dashboard')
 if request.method=='POST':
  c=db();u=c.execute('SELECT * FROM users WHERE username=? AND password=?',(request.form['username'],request.form['password'])).fetchone();c.close()
  if u:session['user']=u['username'];session['mode']=u['mode'];return redirect('/dashboard')
 return page('''<div class="panel login"><h1>🤖 BizBuddy AI</h1><p class="muted">Autonomous AI Business Analyst</p><form method="post"><input name="username" placeholder="Username" required><input type="password" name="password" placeholder="Password" required><button>Login</button></form><b>Demo:</b> admin / BizBuddy@2026</div>''')
@app.route('/logout')
def logout():session.clear();return redirect('/')
@app.route('/dashboard')
def dashboard():
 if not session.get('user'):return redirect('/')
 r,e,p,low,best=analysis();rec,alerts,f,a=agent();mode=session.get('mode','professional')
 if mode=='simple':
  x=f'<h1>Good Morning 👋</h1><p class="muted">Simple Business Mode</p><div class="cards"><div class="card">Sales<div class="value">₹{r:,.0f}</div></div><div class="card">Expenses<div class="value">₹{e:,.0f}</div></div><div class="card">Earnings<div class="value">₹{p:,.0f}</div></div><div class="card">Best Seller<div class="value">{best}</div></div></div><div class="panel"><h2>🤖 BizBuddy Suggests</h2>'+''.join('<p>💡 '+z+'</p>' for z in rec)+'</div>'
 else:
  x=f'<h1>BizBuddy AI Dashboard</h1><p class="muted">Professional Mode — Autonomous Business Intelligence</p><div class="cards"><div class="card">Revenue<div class="value">₹{r:,.0f}</div></div><div class="card">Expenses<div class="value">₹{e:,.0f}</div></div><div class="card">Profit<div class="value">₹{p:,.0f}</div></div><div class="card">Forecast<div class="value">₹{f:,.0f}</div></div><div class="card">Low Stock<div class="value">{low}</div></div><div class="card">Anomalies<div class="value">{len(a)}</div></div></div><div class="panel"><h2>🤖 Autonomous AI Agent</h2>'+''.join('<p>💡 <b>Recommendation:</b> '+z+'</p>' for z in rec)+'</div>'
  if alerts:x+='<div class="panel"><h2>🚨 Proactive Alerts</h2>'+''.join(f'<div class="alert"><b>{t}</b><p>{m}</p><p><b>Action:</b> {q}</p><span class="badge">{s}</span></div>' for t,m,s,q in alerts)+'</div>'
 return page(x)
@app.route('/upload',methods=['GET','POST'])
def upload():
 if not session.get('user'):return redirect('/')
 msg=''
 if request.method=='POST':
  try:
   f=request.files['file'];typ=request.form['type'];d=pd.read_csv(f);c=db()
   if typ=='sales':
    req=['date','product','quantity','price'];assert all(z in d.columns for z in req),'Sales CSV: date,product,quantity,price';d['date']=pd.to_datetime(d.date,errors='coerce');d['quantity']=pd.to_numeric(d.quantity,errors='coerce').fillna(0);d['price']=pd.to_numeric(d.price,errors='coerce').fillna(0);d=d.dropna(subset=['date']);d['revenue']=d.quantity*d.price
    for _,z in d.iterrows():c.execute('INSERT INTO sales(date,product,quantity,price,revenue) VALUES(?,?,?,?,?)',(str(z.date.date()),str(z.product),float(z.quantity),float(z.price),float(z.revenue)))
   elif typ=='expenses':
    req=['date','category','amount'];assert all(z in d.columns for z in req),'Expenses CSV: date,category,amount';d['date']=pd.to_datetime(d.date,errors='coerce');d['amount']=pd.to_numeric(d.amount,errors='coerce').fillna(0);d=d.dropna(subset=['date'])
    for _,z in d.iterrows():c.execute('INSERT INTO expenses(date,category,amount) VALUES(?,?,?)',(str(z.date.date()),str(z.category),float(z.amount)))
   else:
    req=['product','stock','reorder_level'];assert all(z in d.columns for z in req),'Inventory CSV: product,stock,reorder_level'
    for _,z in d.iterrows():c.execute('INSERT INTO inventory(product,stock,reorder_level) VALUES(?,?,?)',(str(z.product),float(z.stock),float(z.reorder_level)))
   c.commit();c.close();msg='Upload successful.'
  except Exception as ex:msg='Upload error: '+str(ex)
 return page(f'''<h1>📤 Upload Data</h1><div class="panel"><form method="post" enctype="multipart/form-data"><select name="type"><option value="sales">Sales</option><option value="expenses">Expenses</option><option value="inventory">Inventory</option></select><input type="file" name="file" accept=".csv" required><button>Upload & Analyse</button></form><b>{msg}</b><hr><p>Sales: date,product,quantity,price</p><p>Expenses: date,category,amount</p><p>Inventory: product,stock,reorder_level</p></div>''')
@app.route('/alerts')
def alerts_page():
 if not session.get('user'):return redirect('/')
 _,a,_,_=agent();return page('<h1>🚨 Proactive Alerts</h1><div class="panel">'+(''.join(f'<div class="alert"><b>{t}</b><p>{m}</p><p><b>Action:</b> {q}</p><span class="badge">{s}</span></div>' for t,m,s,q in a) or '<p>No major alerts detected.</p>')+'</div>')
@app.route('/mode',methods=['GET','POST'])
def mode():
 if not session.get('user'):return redirect('/')
 if request.method=='POST':
  m=request.form['mode'];c=db();c.execute('UPDATE users SET mode=? WHERE username=?',(m,session['user']));c.commit();c.close();session['mode']=m;return redirect('/dashboard')
 m=session.get('mode','professional');return page(f'<h1>⚙️ Business Mode</h1><div class="panel"><form method="post"><select name="mode"><option value="professional" {"selected" if m=="professional" else ""}>Professional Mode</option><option value="simple" {"selected" if m=="simple" else ""}>Simple Mode</option></select><button>Save Mode</button></form></div>')
init()
if __name__=='__main__':app.run(host='0.0.0.0',port=int(os.getenv('PORT',5000)),debug=True)
