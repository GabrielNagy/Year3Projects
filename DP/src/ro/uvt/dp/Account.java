package ro.uvt.dp;

/**
 * Class use to store account information
 *
 */
public abstract class Account implements Operations {

	protected String accountIBAN = null;
	protected double amount = 0;

	public static enum TYPE {
		EUR, RON
	}

	protected Account(String accountIBAN, double amount) {
		this.accountIBAN = accountIBAN;
		deposit(amount);
	}

	@Override
	public double getTotalAmount() {

		return amount + amount * getInterest();
	}

	@Override
	public void deposit(double suma) {

		this.amount += suma;
	}

	@Override
	public void withdraw(double suma) {

		this.amount -= suma;
	}

	public String toString() {
		return "Account: code=" + accountIBAN + ", amount=" + amount;
	}

	public String getAccountNumber() {
		return accountIBAN;
	}

}
