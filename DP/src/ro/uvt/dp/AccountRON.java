package ro.uvt.dp;

public class AccountRON extends Account implements Transfer {

	public AccountRON(String accountIBAN, double amount) {
		super(accountIBAN, amount);
	}

	public double getInterest() {
		if (amount < 500)
			return 0.03;
		else
			return 0.08;

	}

	@Override
	public String toString() {
		return "Account RON [" + super.toString() + "]";
	}

	@Override
	public void transfer(Account c, double s) {
		c.withdraw(s);
		deposit(s);
	}
}
