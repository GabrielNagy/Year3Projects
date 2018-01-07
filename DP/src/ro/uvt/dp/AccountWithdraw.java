package ro.uvt.dp;

public class AccountWithdraw implements AccountCommand {
    Account acc;
    double sum;

    public AccountWithdraw(Account acc, double sum) {
        this.acc = acc;
        this.sum = sum;
    }

    @Override
    public void execute(){
        this.acc.withdraw(sum);
    }
}
