import java.util.Scanner;

public class Introvert{

    static int[] current = {10,10,10,10,10};
    static int[] potentialProduction = new int[5];
    static boolean alive = true;

    public static void main(String[] args){
        Scanner s = new Scanner(System.in);
        String input = s.nextLine();
        String[] inputArray = input.split(",");
        for(int i = 0; i < 5; i++){
            potentialProduction[i] = Integer.parseInt(inputArray[i].replaceAll("\\D+",""));
        }

        while(alive){
            int pos = decideProduction();
            produce(pos);
            System.out.println("L");
            for(int i = 0; i < 5; i++){
                current[i] -= 2;
                if(current[i] < 0)
                    alive = false;
            }
        }
        s.nextLine(); //read final `q` message
    }

    public static int decideProduction(){
        int lowestPotential = 9999;
        int lowestPotentialPosition = 9999;
        for(int i = 0; i < 5; i++){
            if(current[i] == 2 || current[i] == 3){
                lowestPotentialPosition = i;
                break;
            }
            int potential = current[i] + potentialProduction[i];
            if(potential < lowestPotential){
                lowestPotential = potential;
                lowestPotentialPosition = i;
            }
        }
        switch(lowestPotentialPosition){
            case 0: System.out.println("A"); return 0;
            case 1: System.out.println("B"); return 1;
            case 2: System.out.println("C"); return 2;
            case 3: System.out.println("D"); return 3;
            case 4: System.out.println("E"); return 4;
            default: System.out.println("A"); return 0;
        }
    }

    public static void produce(int pos){
        current[pos] += potentialProduction[pos];
    }

}