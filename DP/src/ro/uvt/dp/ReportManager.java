package ro.uvt.dp;

import java.io.*;

public final class ReportManager {

    public static void addEntry(String bankCode, String msg) {

        try(FileWriter fw = new FileWriter("logs/" + bankCode + ".log", true);
             BufferedWriter bw = new BufferedWriter(fw);
             PrintWriter out = new PrintWriter(bw))
        {
            out.println(msg);
        } catch (IOException e) {
            System.out.println("Something went wrong when opening file.");
        }
    }

    // Outputs the log of the specified bank to the console
    public static void readLog(String bankCode) {
        try{
            BufferedReader in = new BufferedReader(new FileReader("logs/" + bankCode + ".log"));
            System.out.println("Showing logs of bank with ID " + bankCode);
            while(in.ready()) {
                System.out.println(in.readLine());
            }
        } catch (Exception e) {
            System.out.println("Something went wrong when reading file.");
        }
    }

    public static void purgeAll() {
        File folder =  new File("logs/");
        File[] listOfFiles = folder.listFiles();

        for (int i = 0; i < listOfFiles.length; i++) {
            if (listOfFiles[i].isFile() && listOfFiles[i].getName().endsWith(".log")) {
                listOfFiles[i].delete();
            }
        }
    }

    public static void createLog(String bankCode) {
        File file = new File("logs/" + bankCode + ".log");
        try{
            if(!file.createNewFile()){
                file.delete();
                file.createNewFile();
            }
        }  catch (Exception e) {
            System.out.println("Something went wrong when opening file.");
        }
    }
}
