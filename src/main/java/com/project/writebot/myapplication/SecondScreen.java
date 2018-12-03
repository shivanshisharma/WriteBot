package com.project.writebot.myapplication;

import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.app.ActionBar;
import android.view.View;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.ToggleButton;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;

public class SecondScreen extends AppCompatActivity {
    ActionBar actionBar;
    private DatagramSocket socket;
    private InetAddress serverAddress;
    private int serverPort;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Thread listenThread = new Thread(new Runnable() {
            @Override
            public void run() {
                configureSocket();
                listen();
            }
        });
        listenThread.start();
        actionBar = getSupportActionBar();
        actionBar.setBackgroundDrawable(new ColorDrawable(Color.parseColor("#FF000000")));

        Button button = findViewById(R.id.button2);
        button.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {
                storeText();
            }
        });
        ToggleButton toggle = (ToggleButton) findViewById(R.id.toggleButton);
        TextView tt = (TextView) findViewById(R.id.toggleButton);
        toggle.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if(isChecked){
                    startRecording();
                }
                else{
                    stopRecording();
                }
            }
        });
        ToggleButton togglepart2 = (ToggleButton) findViewById(R.id.toggleButton2);
        TextView ttpart2 = (TextView) findViewById(R.id.toggleButton2);
        togglepart2.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if(isChecked){
                    startWriting();
                }
                else{
                    stopWriting();
                }
            }
        });
    }

    private void configureSocket() {
        try {
            this.socket = new DatagramSocket();
            this.serverAddress = InetAddress.getByName("172.20.10.8");
            this.serverPort = 1069;
        } catch(Exception e) {
            System.out.println(e);
        }
    }

    private void listen() {
        while (true) {
            try {
                byte[] buffer = new byte[1024];
                DatagramPacket receivePacket = new DatagramPacket(buffer, buffer.length);
                System.out.println("Listening" + this.socket.getLocalPort());
                this.socket.receive(receivePacket);
                System.out.println("Received Packet");
                processPacket(receivePacket);

            } catch (Exception e) {
                System.out.println(e);
            }
        }
    }

    private void processPacket(DatagramPacket packet) {
        try {
            String receivedString = new String(packet.getData(), "UTF-8").substring(0, packet.getLength());
            String opcode = receivedString.substring(0, 2);
            String message = receivedString.substring(2);
            System.out.println(" Opcode: " + opcode + "Message: " + message);
            processCommand(opcode, message);
        } catch (Exception e) {
            System.out.println(e);
        }
    }

    private void processCommand(String opcode, String message) {
        switch (opcode) {
            case "06":
                System.out.println("Showing text");
                EditText textView = findViewById(R.id.editText);
                textView.setText(message);
            case "09":
                System.out.println("Received ACK for command with opcode " + opcode);
                break;
                default:
                    System.out.println("Not supported");
        }
    }

    private void startRecording() {
        String opCode = "01";
        sendMessageOnNewThread(opCode);
    }

    private void stopRecording() {
        String opCode = "02";
        sendMessageOnNewThread(opCode);
    }

    private void storeText() {
        TextView textView = findViewById(R.id.editText);
        String newText = textView.getText().toString();
        String opCode = "03";
        sendMessageOnNewThread(opCode + newText);
    }

    private void startWriting() {
        String opCode = "04";
        sendMessageOnNewThread(opCode);
    }

    private void stopWriting() {
        String opCode = "05";
        sendMessageOnNewThread(opCode);
    }

    private void sendMessageOnNewThread(final String message) {
        Thread thread = new Thread(new Runnable() {
            @Override
            public void run() {
                sendMessage(message);
            }
        });
        thread.start();
    }

    private void sendMessage(String message) {
        byte[] data = message.getBytes();
        DatagramPacket sendPacket = new DatagramPacket(data, data.length, this.serverAddress, this.serverPort);
        try {
            System.out.println(InetAddress.getLocalHost().getHostAddress());
            this.socket.send(sendPacket);
        } catch(Exception e) {
            System.out.println(e);
        }
    }
}
