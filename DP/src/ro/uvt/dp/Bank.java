package ro.uvt.dp;

import java.util.ArrayList;

/**
 * 
 * Class used to store the information about the bank clients and operations
 *
 */
public class Bank {

	private final static int MAX_CLIENTS_NUMBER = 100;
	private String bankCode = null;

	private ArrayList<Client> clients = new ArrayList<>();

	public Bank(String codBanca) {
		this.bankCode = codBanca;
		ReportManager.createLog(bankCode);
	}

	public void addClient(Client c) {
		if(clients.size() + 1 <= MAX_CLIENTS_NUMBER)
		{
			clients.add(c);
			ReportManager.addEntry(bankCode, "Added Client: " + c.toString());
		} else {
			ReportManager.addEntry(bankCode, "Attempted to add client but client list is full.");
		}
	}

	public void removeClient(Client c) {
		if(c != null && clients.contains(c)){
			clients.remove(c);
			ReportManager.addEntry(bankCode, "Removed Client: " + c.toString());
		} else {
			ReportManager.addEntry(bankCode, "Attempted to remove client that doesn't exist.");
		}
	}

	public Client getClient(String name) {
		for(Client c : clients)
		{
			if(c.getName().equals(name)){
				return c;
			}
		}

		return null;
	}

	@Override
	public String toString() {
		return "Bank [code=" + bankCode + ", clients=" + clients.toString() + "]";
	}

}
