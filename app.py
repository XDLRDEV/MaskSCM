from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import drawSupplyChain
import sys
import os
import time
import datetime

sys.path.append('../python-sdk/')
from call_console import execute as run

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

cname = 'SupplyChain'
caddr = '0x84139e0d46160aa2dd2541f499049095596891c9'
call = 'call'
send = 'sendtx'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin':
            session['id'] = caddr
            session['username'] = '管理员'
            session['type'] = 0
            return redirect(url_for('index'))
        supplier_list = run([call, cname, caddr, 'GetSupplierList'])[0]
        for supplier_id in supplier_list:
            supplier = run([call, cname, caddr, 'GetSupplierInfo', supplier_id])
            if supplier[0] == request.form['username']:
                session['id'] = supplier_id
                session['username'] = supplier[0]
                session['type'] = supplier[1]
                return redirect(url_for('index'))
        return render_template("login.html", error=1)
    return render_template("login.html", error=0)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        user = {}
        user['id'] = session['id']
        user['username'] = session['username']
        user['type'] = session['type']
        if user['id'] != caddr:
            user['balance'] = run([call, cname, caddr, 'GetSupplierBalance', user['id']])[0]
            user['stn'] = run([call, cname, caddr, 'GetSupplierStuck', user['id']])[0]
            user['loan'] = run([call, cname, caddr, 'GetSupplierLoan', user['id']])[0]
            supplier_list = run([call, cname, caddr, 'GetSupplierList'])[0]
            return render_template("index.html", user=user, sp_num=len(supplier_list))
        else:
            import _thread
            drawSupplyChain.__init()
            _thread.start_new_thread(drawSupplyChain.program, ())
            return render_template("index.html", user=user)
    else:
        return redirect(url_for('login'))


@app.route('/get_option', methods=['POST'])
def get_option():
    u_list = drawSupplyChain.get_list()
    return jsonify(u_list)


@app.route('/get_option_ex', methods=['POST'])
def get_option_ex():
    u_list = drawSupplyChain.get_list_ex()
    return jsonify(u_list)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'username' in session:
        if session['type'] != 0:
            return redirect(url_for('index'))
        user = {}
        user['id'] = session['id']
        user['username'] = session['username']
        user['type'] = session['type']
        supplier_list = list(run([call, cname, caddr, 'GetSupplierList'])[0])
        if request.method == 'POST':
            if request.form['username'] == '':
                return render_template("add_user.html", user=user, error=2, slist=supplier_list)
            supplier_id = run([send, cname, caddr, 'CreateSupplier', request.form['username'], request.form['type']])[0]
            if supplier_id in supplier_list:
                supplier_list.remove(supplier_id)
            if supplier_id == '0x0000000000000000000000000000000000000000':
                return render_template("add_user.html", user=user, error=1, slist=supplier_list)
            for sp in supplier_list:
                if sp != supplier_id:
                    if 'prior' + sp in request.form:
                        run([send, cname, caddr, 'LinkSupplier', sp, supplier_id])
                    elif 'next' + sp in request.form:
                        run([send, cname, caddr, 'LinkSupplier', supplier_id, sp])
            return render_template("add_user.html", user=user, error=-1, slist=supplier_list,
                                   au=request.form['username'], au_id=supplier_id)
        return render_template("add_user.html", user=user, error=0, slist=supplier_list)
    else:
        return redirect(url_for('login'))


@app.route('/del_user', methods=['GET', 'POST'])
def del_user():
    if 'username' in session:
        if session['type'] != 0:
            return redirect(url_for('index'))
        user = {}
        user['id'] = session['id']
        user['username'] = session['username']
        user['type'] = session['type']
        if request.method == 'POST':
            if request.form['username'] == '':
                return render_template("del_user.html", user=user, error=2)
            if run([send, cname, caddr, 'DeleteSupplier', request.form['username']])[0]:
                return render_template("del_user.html", user=user, error=-1, au=request.form['username'])
            else:
                return render_template("del_user.html", user=user, error=1)
        return render_template("del_user.html", user=user, error=0)
    else:
        return redirect(url_for('login'))


@app.route('/list_user', methods=['GET', 'POST'])
def list_user():
    if 'username' in session:
        if session['type'] != 0:
            return redirect(url_for('index'))
        user = {}
        user['id'] = session['id']
        user['username'] = session['username']
        user['type'] = session['type']

        userlist = [[caddr, '管理员', 0, '']]
        supplier_list = run([call, cname, caddr, 'GetSupplierList'])[0]
        for supplier_id in supplier_list:
            supplier = run([call, cname, caddr, 'GetSupplierInfo', supplier_id])
            balance = run([call, cname, caddr, 'GetSupplierBalance', supplier_id])
            u = [supplier_id, supplier[0], supplier[1], balance[0]]
            userlist.append(u)
        return render_template("list_user.html", user=user, userlist=userlist)
    else:
        return redirect(url_for('login'))


@app.route('/edit_balance', methods=['GET', 'POST'])
def edit_balance():
    if 'username' in session:
        if session['type'] != 0:
            return redirect(url_for('index'))
        user = {}
        user['id'] = session['id']
        user['username'] = session['username']
        user['type'] = session['type']
        if request.method == 'POST':
            if request.form['id'] == '':
                return render_template("edit_balance.html", user=user, error=2)
            if run([send, cname, caddr, 'ChangeBalance', request.form['id'], request.form['delta']])[0]:
                return render_template("edit_balance.html", user=user, error=-1, au=request.form['id'])
            else:
                return render_template("edit_balance.html", user=user, error=1)
        return render_template("edit_balance.html", user=user, error=0)
    else:
        return redirect(url_for('login'))


@app.route('/produce_stuck', methods=['GET', 'POST'])
def produce_stuck():
    if 'username' in session:
        if session['type'] == 0:
            return redirect(url_for('index'))
        user = {}
        user['id'] = session['id']
        user['username'] = session['username']
        user['type'] = session['type']
        if request.method == 'POST':
            if request.form['num'] == '':
                return render_template("produce_stuck.html", user=user, error=2)
            if request.form['name'] == '':
                return render_template("produce_stuck.html", user=user, error=3)
            stuck_id = run([send, cname, caddr, 'CreateStuck', user['id'], request.form['num'], request.form['name'],
                            int(time.mktime(datetime.datetime.now().timetuple()))])[0]
            if stuck_id == '0x0000000000000000000000000000000000000000':
                return render_template("produce_stuck.html", user=user, error=1)
            else:
                return render_template("produce_stuck.html", user=user, error=-1, au=stuck_id)
        return render_template("produce_stuck.html", user=user, error=0)
    else:
        return redirect(url_for('login'))


@app.route('/del_stuck', methods=['GET', 'POST'])
def del_stuck():
    if 'username' in session:
        if session['type'] == 0:
            return redirect(url_for('index'))
        user = {}
        user['id'] = session['id']
        user['username'] = session['username']
        user['type'] = session['type']
        if request.method == 'POST':
            if request.form['id'] == '':
                return render_template("del_stuck.html", user=user, error=2)
            if run([send, cname, caddr, 'DeleteStuck', user['id'], request.form['id'],
                    int(time.mktime(datetime.datetime.now().timetuple()))])[0]:
                return render_template("del_stuck.html", user=user, error=-1, au=request.form['id'])
            else:
                return render_template("del_stuck.html", user=user, error=1)
        return render_template("del_stuck.html", user=user, error=0)
    else:
        return redirect(url_for('login'))


@app.route('/list_stuck', methods=['GET', 'POST'])
def list_stuck():
    if 'username' in session:
        if session['type'] == 0:
            return redirect(url_for('index'))
        user = {}
        user['id'] = session['id']
        user['username'] = session['username']
        user['type'] = session['type']
        user['stn'] = run([call, cname, caddr, 'GetSupplierStuck', user['id']])[0]

        stucklist = []
        for stuck_id in user['stn']:
            stuck = run([call, cname, caddr, 'GetStuckInfo', stuck_id])
            u = [stuck_id, stuck[0], stuck[1]]
            stucklist.append(u)
        return render_template("list_stuck.html", user=user, stucklist=stucklist)
    else:
        return redirect(url_for('login'))


@app.route('/transfer_stuck', methods=['GET', 'POST'])
def transfer_stuck():
    if 'username' in session:
        if session['type'] == 0:
            return redirect(url_for('index'))
        user = {}
        user['id'] = session['id']
        user['username'] = session['username']
        user['type'] = session['type']
        user['stn'] = run([call, cname, caddr, 'GetSupplierStuck', user['id']])[0]

        if request.method == 'POST':
            if request.form['num'] == '':
                return render_template("transfer_stuck.html", user=user, error=2)
            if request.form['name'] == '':
                return render_template("transfer_stuck.html", user=user, error=3)
            stuck_id = run([send, cname, caddr, 'CreateStuck', user['id'], request.form['num'], request.form['name'],
                            int(time.mktime(datetime.datetime.now().timetuple()))])[0]
            if stuck_id == '0x0000000000000000000000000000000000000000':
                return render_template("transfer_stuck.html", user=user, error=1)
            else:
                for s in user['stn']:
                    if s in request.form:
                        run([send, cname, caddr, 'AddMaterials', user['id'], s, stuck_id])
                        run([send, cname, caddr, 'DeleteStuck', user['id'], s,
                             int(time.mktime(datetime.datetime.now().timetuple()))])
                return render_template("transfer_stuck.html", user=user, error=-1, au=stuck_id)
        return render_template("transfer_stuck.html", user=user, error=0)
    else:
        return redirect(url_for('login'))


@app.route('/shop', methods=['GET', 'POST'])
def shop():
    if 'username' in session:
        if session['type'] == 0:
            return redirect(url_for('index'))
        user = {}
        user['id'] = session['id']
        user['username'] = session['username']
        user['type'] = session['type']
        userlist = []
        supplier_list = run([call, cname, caddr, 'GetSupplierRelation', user['id']])[0]
        for supplier_id in supplier_list:
            if supplier_id != user['id']:
                supplier = run([call, cname, caddr, 'GetSupplierInfo', supplier_id])
                u = [supplier_id, supplier[0], supplier[1]]
                userlist.append(u)
        return render_template("shop.html", user=user, userlist=userlist)
    else:
        return redirect(url_for('login'))


@app.route('/shop/<string:id>')
def shop_ex1(id):
    if 'username' in session:
        if session['type'] == 0:
            return redirect(url_for('index'))
        user = {}
        user['id'] = session['id']
        user['username'] = session['username']
        user['type'] = session['type']

        stn = run([call, cname, caddr, 'GetSupplierStuck', id])[0]

        stucklist = []
        for stuck_id in stn:
            stuck = run([call, cname, caddr, 'GetStuckInfo', stuck_id])
            u = [stuck_id, stuck[0], stuck[1]]
            stucklist.append(u)
        return render_template("shop_stuck.html", user=user, stucklist=stucklist, sid=id)
    else:
        return redirect(url_for('login'))


@app.route('/buy/<string:sid>/<string:uid>', methods=['GET', 'POST'])
def buy(sid, uid):
    if 'username' in session:
        if session['type'] == 0:
            return redirect(url_for('index'))
        user = {}
        user['id'] = session['id']
        user['username'] = session['username']
        user['type'] = session['type']
        user['loan'] = run([call, cname, caddr, 'GetSupplierLoan', user['id']])[0]
        llist = []
        for ll in user['loan']:
            sp = run([call, cname, caddr, 'GetLoanSp', ll])[0]
            if sid in sp:
                llist.append(ll)
        if request.method == 'POST':
            if request.form['price'] == '':
                return render_template("buy.html", user=user, error=2, llist=llist)
            if request.form['sp'] == '0':
                deal_id = run([send, cname, caddr, 'makeDeal', sid, user['id'], request.form['price'], uid,
                               int(time.mktime(datetime.datetime.now().timetuple()))])[0]
            else:
                deal_id = run([send, cname, caddr, 'LoanDeal', sid, user['id'], request.form['price'], uid,
                               int(time.mktime(datetime.datetime.now().timetuple())), request.form['sp']])[0]
            if deal_id == '0x0000000000000000000000000000000000000000':
                return render_template("buy.html", user=user, error=1, llist=llist)
            return render_template("buy.html", user=user, error=-1, llist=llist, au=deal_id)
        return render_template("buy.html", user=user, error=0, llist=llist)


@app.route('/add_loan', methods=['GET', 'POST'])
def add_loan():
    if 'username' in session:
        if session['type'] != 0:
            return redirect(url_for('index'))
        user = {}
        user['id'] = session['id']
        user['username'] = session['username']
        user['type'] = session['type']
        supplier_list = run([call, cname, caddr, 'GetSupplierList'])[0]
        if request.method == 'POST':
            if request.form['money'] == '':
                return render_template("add_loan.html", user=user, error=2, sp_list=supplier_list)
            if request.form['sp'] == '':
                return render_template("add_loan.html", user=user, error=3, sp_list=supplier_list)
            loan_id = run([send, cname, caddr, 'CreateLoan', request.form['money'], request.form['sp'],
                           int(time.mktime(datetime.datetime.now().timetuple()))])[0]
            if loan_id == '0x0000000000000000000000000000000000000000':
                return render_template("add_loan.html", user=user, error=1, sp_list=supplier_list)
            for sp in supplier_list:
                if sp in request.form:
                    run([send, cname, caddr, 'AddLoanSupplier', loan_id, sp])
            return render_template("add_loan.html", user=user, error=-1, sp_list=supplier_list, au=loan_id)
        return render_template("add_loan.html", user=user, error=0, sp_list=supplier_list)
    else:
        return redirect(url_for('login'))


@app.route('/list_loan', methods=['GET', 'POST'])
def list_loan():
    if 'username' in session:
        if session['type'] == 0:
            loanlist = run([call, cname, caddr, 'GetLoanList'])[0]
        else:
            loanlist = run([call, cname, caddr, 'GetSupplierLoan', session['id']])[0]
        user = {}
        user['id'] = session['id']
        user['username'] = session['username']
        user['type'] = session['type']

        llist = []
        for loan in loanlist:
            l = run([call, cname, caddr, 'GetLoanInfo', loan])
            print(l)
            u = [l[0], l[1], datetime.datetime.fromtimestamp(l[2]).strftime("%Y-%m-%d %H:%M:%S")]
            print(u)
            llist.append(u)
        return render_template("list_loan.html", user=user, llist=llist)
    else:
        return redirect(url_for('login'))


@app.route('/trace/<string:s_id>')
def trace(s_id):
    if 'username' in session:
        user = {}
        user['id'] = session['id']
        user['username'] = session['username']
        user['type'] = session['type']
        import _thread
        drawSupplyChain.__init()
        _thread.start_new_thread(drawSupplyChain.program_ex, (s_id,))
        return render_template("trace.html", user=user)
    else:
        return redirect(url_for('login'))


@app.route('/trace', methods=['POST', 'GET'])
def trace_ex():
    if 'username' in session:
        user = {}
        user['id'] = session['id']
        user['username'] = session['username']
        user['type'] = session['type']
        if request.method == 'POST':
            return redirect(url_for('trace', s_id=request.form['sid']))
        return render_template("trace_ex.html", user=user)
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
