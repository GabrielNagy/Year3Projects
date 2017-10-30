package ro.uvt.dp;

import java.util.Arrays;
import java.time.LocalDate;

import ro.uvt.dp.TYPE;

public class Client {
	public static final int NUMAR_MAX_CONTURI = 5;

	private final String name;
	private final String address;
	private final Account accounts[];
	private final int accountsNr = 0;
	private final String dateOfBirth;

	private Client(ClientBuilder builder) {
		this.name = builder.name;
		this.address = builder.address;
		this.accounts = builder.accounts;
		this.dateOfBirth = builder.dateOfBirth;
	}

	public static class ClientBuilder {
		private final String name;
		private final String address;
		private final Account accounts[];
		private String dateOfBirth;
		
		public ClientBuilder(String name, String address, Account accounts[]) {
			this.name = name;
			this.address = address;
			this.accounts = new Account[NUMAR_MAX_CONTURI];
		}
		
		public ClientBuilder dob(String dateOfBirth) {
			this.dateOfBirth = dateOfBirth;
			return this;
		}
		
		public Client build() {
			return new Client(this);
		}
	}
	
	public Client(String nume, String adresa, TYPE tip, String numarCont, double suma) {
		this.name = nume;
		this.address = adresa;
		accounts = new Account[NUMAR_MAX_CONTURI];
		addAccount(tip, numarCont, suma);
	}

	public void addAccount(TYPE tip, String numarCont, double suma) {
		Account c = null;
		if (tip == TYPE.EUR)
			c = new ContEUR(numarCont, suma);
		else if (tip == TYPE.RON)
			c = new AccountRON(numarCont, suma);
		accounts[accountsNr++] = c;
	}

	public Account getAccount(String accountCode) {
		for (int i = 0; i < accountsNr; i++) {
			if (accounts[i].getAccountNumber().equals(accountCode)) {
				return accounts[i];
			}
		}
		return null;
	}

	@Override
	public String toString() {
		return "\n\tClient [name=" + name + ", address=" + address + ", acounts=" + Arrays.toString(accounts) + "]";
	}

	public String getName() {
		return name;
	}
	
	public String getAddress() {
		return address;
	}

	public String getDateOfBirth() {
		return dateOfBirth;
	}
}
