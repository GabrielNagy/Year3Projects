package ro.uvt.dp;

/**
 * 
 * Euro account type
 *
 */
public class AccountEUR extends Account {

	public AccountEUR(String accountIBAN, double amount) {
		super(accountIBAN, amount);
	}

	public double getInterest() {
		return 0.01;

	}

	@Override
	public String toString() {
		return "Account EUR [" + super.toString() + "]";
	}
}
