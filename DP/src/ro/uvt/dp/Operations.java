package ro.uvt.dp;

public interface Operations {
	double getTotalAmount();

	double getInterest();

	void deposit(double amount);

	void withdraw(double amount);
}
