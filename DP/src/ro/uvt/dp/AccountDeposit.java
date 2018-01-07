package ro.uvt.dp;

public class AccountDeposit implements AccountCommand{

    Account acc;
    double sum = 0;

    public AccountDeposit(Account acc, double sum)
    {
        this.acc = acc;
        this.sum = sum;
    }

    @Override
    public void execute() {
        this.acc.deposit(sum);
    }
}
