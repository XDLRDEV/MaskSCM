pragma solidity^0.4.25;

contract SupplyChain{

    //供应商（包括农户、各级供应商、用粮厂商）
    struct Supplier{
        address SupplierID;
        string SupplierName;
        uint8 kind;
        uint balance;
        address[] stuck;
        address[] loan;
        address[] prior;
        address[] next;
    }

    //放贷银行
    struct Bank{
        address[] loan;
    }

    //货品批号
    struct Stuck{
        address id;
        uint num;
        string stuff;
        address[] sp;
        uint[] time;
        address[] from;
        address[] turn;
    }

    //贷款批号
    struct Loan{
        address id;
        uint num;
        address sp;
        address[] suppliers;
        uint time;
    }

    //物流批号
    struct DealInfo{
        address id;
        address sp;
        address by;
        uint money;
        address st;
        uint time;
    }

    address[] SupplierList = new address[](0);
    mapping(address => Supplier) supplier;
    mapping(address => Stuck) stuck;
    mapping(address => Loan) loan;
    mapping(address => DealInfo) deal;
    Bank bank;

    event NewSupplier(address id);
    event DelSupplier(address id);
    event NewLoan(address id, uint money, address sp);
    event NewStuck(address id, address sp, uint num, string stuff, uint time);
    event DelStuck(address id, uint time);
    event Deal(address id, address sp, address by, uint money,address st, uint time);

    //返回用户列表
    function GetSupplierList() public view returns(address[]){
        return SupplierList;
    }

    //查看用户信息
    function GetSupplierInfo(address id) public view returns(string,uint8){
        return(supplier[id].SupplierName, supplier[id].kind);
    }

    //查询用户余额
    function GetSupplierBalance(address id) public view returns(uint){
        return supplier[id].balance;
    }

    //查询用户存货
    function GetSupplierStuck(address id) public view returns(address[]){
        return supplier[id].stuck;
    }

    //查询用户贷款
    function GetSupplierLoan(address id) public view returns(address[]){
        return supplier[id].loan;
    }

    //查询库存信息
    function GetStuckInfo(address id) public view returns(uint num, string name){
        return(stuck[id].num,stuck[id].stuff);
    }

    //查询库存物流
    function GetStuckFlew(address id) public view returns(address[] sp, uint[] time){
        return(stuck[id].sp,stuck[id].time);
    }

    //查询物流信息
    function GetDealInfo(address id) public view returns(address,address,uint,address,uint){
        return(deal[id].sp,deal[id].by,deal[id].money,deal[id].st,deal[id].time);
    }

    //查询产品加工信息
    function GetMakeInfo(address id) public view returns(address[], address[]){
        return(stuck[id].from,stuck[id].turn);
    }

    //查询所有贷款
    function GetLoanList() public view returns(address[]){
        return bank.loan;
    }

    //查询贷款信息
    function GetLoanInfo(address id) public view returns(uint, address, uint){
        return(loan[id].num,loan[id].sp,loan[id].time);
    }

    //查询贷款限制购买厂商
    function GetLoanSp(address id) public view returns(address[]){
        return loan[id].suppliers;
    }

    //链上关系查询
    function GetSupplierRelation(address id) public returns(address[], address[]){
        return(supplier[id].prior,supplier[id].next);
    }

    //bytes32 转 address
    function bytesToAddress(bytes32 bys) public pure returns (address) {
        return address(uint160(uint256(bys)));
    }

    //判断用户是否存在
    function ExistSupplier(address id) public constant returns (bool){
		if(supplier[id].SupplierID == id){
			return true;
		}else{
			return false;
		}
	}

    //新建用户
    function CreateSupplier(string name,uint8 kind) public returns (address) {
		address id = bytesToAddress(sha256(abi.encodePacked(name,kind)));
        if(ExistSupplier(id)){
			return 0;
		}
        SupplierList.length++;
        SupplierList[SupplierList.length-1]=id;
		supplier[id] = Supplier(id,name,kind,0,new address[](0),new address[](0),new address[](0),new address[](0));
        emit NewSupplier(id);
		return id;
	}

    //删除用户
    function DeleteSupplier(address id) public returns (bool) {
        if(!ExistSupplier(id)){
			return false;
		}
        uint i;
        uint j;
        for(i=0;i<supplier[id].prior.length;i++){
            for(j=0;j<supplier[supplier[id].prior[i]].next.length;j++){
                if(supplier[supplier[id].prior[i]].next[j] == id){
                    supplier[supplier[id].prior[i]].next[j] = supplier[supplier[id].prior[i]].next[supplier[supplier[id].prior[i]].next.length-1];
                    supplier[supplier[id].prior[i]].next.length--;
                    break;
                }
            }
        }
        for(i=0;i<supplier[id].next.length;i++){
            for(j=0;j<supplier[supplier[id].next[i]].prior.length;j++){
                if(supplier[supplier[id].next[i]].prior[j] == id){
                    supplier[supplier[id].next[i]].prior[j] = supplier[supplier[id].next[i]].prior[supplier[supplier[id].next[i]].prior.length-1];
                    supplier[supplier[id].next[i]].prior.length--;
                    break;
                }
            }
        }
        for(i=0;i<SupplierList.length;i++){
            if(SupplierList[i]==id){
                SupplierList[i]=SupplierList[SupplierList.length-1];
            }
        }
        SupplierList.length--;
        delete supplier[id];
        emit DelSupplier(id);
        return true;
    }

    //链接用户
    function LinkSupplier(address prior, address next) public returns (bool) {
        if(!ExistSupplier(prior)||!ExistSupplier(next)){
            return false;
        }
        supplier[prior].next.length++;
        supplier[prior].next[supplier[prior].next.length-1]=next;
        supplier[next].prior.length++;
        supplier[next].prior[supplier[next].prior.length-1]=prior;
        return true;
    }

    //修改用户余额
    function ChangeBalance(address id,int delta) public returns(bool){
        if(!ExistSupplier(id)){
			return false;
		}
        int bal = int(supplier[id].balance) + delta;
        if(bal < 0){
            return false;
        }else{
            supplier[id].balance = uint(bal);
            return true;
        }
    }

    //普通交易
    function makeDeal(address seller, address buyer, uint money, address stn, uint time) public returns(address) {
        if(supplier[buyer].balance < money){
            return 0;
        }

        supplier[seller].balance += money;
        for(uint i=0;i < supplier[seller].stuck.length; i++){
            if(supplier[seller].stuck[i] == stn){
                supplier[seller].stuck[i]=supplier[seller].stuck[supplier[seller].stuck.length-1];
                supplier[seller].stuck.length-=1;
                break;
            }
        }

        supplier[buyer].balance -= money;
        supplier[buyer].stuck.length++;
        supplier[buyer].stuck[supplier[buyer].stuck.length-1]=stn;

        stuck[stn].sp.length++;
        stuck[stn].sp[stuck[stn].sp.length-1]=buyer;

        stuck[stn].time.length++;
        stuck[stn].time[stuck[stn].time.length-1]=time;

        address id = bytesToAddress(sha256(abi.encodePacked(seller,buyer,money,stn,time)));
        deal[id] = DealInfo(id,seller,buyer,money,stn,time);
        emit Deal(id,seller,buyer,money,stn,time);
        return id;
    }

    //上货
    function CreateStuck(address sp, uint num, string stuff, uint time) public returns(address) {
        address id = bytesToAddress(sha256(abi.encodePacked(num, stuff, time)));
        stuck[id] = Stuck(id, num, stuff, new address[](1), new uint[](1), new address[](0), new address[](0));
        stuck[id].sp[0] = sp;
        stuck[id].time[0] = time;
        supplier[sp].stuck.length++;
        supplier[sp].stuck[supplier[sp].stuck.length-1]=id;
        emit NewStuck(id, sp, num, stuff, time);
        return id;
    }

    //下货
    function DeleteStuck(address sp, address id, uint time) public returns(bool) {
        bool sign = false;
        for(uint i=0;i < supplier[sp].stuck.length; i++){
            if(supplier[sp].stuck[i] == id){
                supplier[sp].stuck[i]=supplier[sp].stuck[supplier[sp].stuck.length-1];
                supplier[sp].stuck.length-=1;
                sign = true;
                DelStuck(id, time);
                break;
            }
        }
        stuck[id].time.length++;
        stuck[id].time[stuck[id].time.length-1]=time;
        return sign;
    }

    //增加加工原材料
    function AddMaterials(address sp, address stnOld, address stnNew) public returns(bool){
        for(uint i=0;i<supplier[sp].stuck.length;i++){
            if(stnOld == supplier[sp].stuck[i]){
                stuck[stnNew].from.length++;
                stuck[stnNew].from[stuck[stnNew].from.length-1]=stnOld;
                stuck[stnOld].turn.length++;
                stuck[stnOld].turn[stuck[stnOld].turn.length-1]=stnNew;
                return true;
            }
        }
        return false;
    }
    
    //放贷
    function CreateLoan(uint money, address sp, uint time) public returns(address){
        address id = bytesToAddress(sha256(abi.encodePacked(money, sp, time)));
        loan[id] = Loan(id, money, sp, new address[](0), time);
        bank.loan.length++;
        bank.loan[bank.loan.length-1] = id;
        supplier[sp].loan.length++;
        supplier[sp].loan[supplier[sp].loan.length-1] = id;
        emit NewLoan(id, money, sp);
        return id;
    }

    //增加贷款商铺
    function AddLoanSupplier(address lid, address sp) public returns(bool){
        loan[lid].suppliers.length++;
        loan[lid].suppliers[loan[lid].suppliers.length-1]=sp;
        return true;
    }

    //贷款消费
    function LoanDeal(address seller, address buyer, uint money, address stn, uint time, address LoanId) public returns(address){
        if(loan[LoanId].num < money){
            return 0;
        }

        supplier[seller].balance += money;
        for(uint i=0;i < supplier[seller].stuck.length; i++){
            if(supplier[seller].stuck[i] == stn){
                supplier[seller].stuck[i]=supplier[seller].stuck[supplier[seller].stuck.length-1];
                supplier[seller].stuck.length-=1;
                break;
            }
        }

        loan[LoanId].num -= money;
        supplier[buyer].stuck.length++;
        supplier[buyer].stuck[supplier[buyer].stuck.length-1]=stn;

        stuck[stn].sp.length++;
        stuck[stn].sp[stuck[stn].sp.length-1]=buyer;

        stuck[stn].time.length++;
        stuck[stn].time[stuck[stn].time.length-1]=time;

        address id = bytesToAddress(sha256(abi.encodePacked(seller,buyer,money,stn,time)));
        deal[id] = DealInfo(id,seller,buyer,money,stn,time);
        emit Deal(id,seller,buyer,money,stn,time);
        return id;
    }
}
