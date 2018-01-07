package ro.uvt.dp;

import java.util.ArrayList;
import java.util.Arrays;

import ro.uvt.dp.Account.TYPE;

/**
 * 
 * Class that is used to store the information about one bank client
 *
 */
public class Client {
	public static final int MAX_ACCOUNT_NUMBER = 5;

	private String name;
	private String address;
	private ArrayList<Account> accounts = new ArrayList<>();
	private String cnp = null;

	public Client(String nume, String adresa, TYPE tip, String numarCont, double suma, String cnp) {
		this.name = nume;
		this.address = adresa;
		this.cnp = cnp;
		addAccount(tip, numarCont, suma);
	}

	public boolean addAccount(TYPE tip, String accountCode, double suma) {
		Account c = null;
		if (tip == Account.TYPE.EUR)
			c = new AccountEUR(accountCode, suma);
		else if (tip == Account.TYPE.RON)
			c = new AccountRON(accountCode, suma);
		if(accounts.size() + 1 <= MAX_ACCOUNT_NUMBER) {
			accounts.add(c);
			return true;
		}
		return false;
	}

	public boolean removeAccount(String accountCode) {
		Account acc = getAccount(accountCode);
		if(accounts.contains(acc) && acc.getTotalAmount() == 0) {
			accounts.remove(acc);
			return true;
		}
		return false;
	}

	public Account getAccount(String accountCode) {
		for(Account a : accounts)
		{
			if(a.getAccountNumber().equals(accountCode)){
				return a;
			}
		}
		return null;
	}


	public String getName() {
		return name;
	}

	@Override
	public String toString() {
		return "\n\tClient [name=" + name + ", cnp=" + cnp + ", address=" + address + ", acounts=" + accounts.toString() + "]";
	}

}
