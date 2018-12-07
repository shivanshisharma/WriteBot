package com.project.writebot.myapplication;

import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.app.ActionBar;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.ToggleButton;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;

public class SecondScreen extends AppCompatActivity implements AdapterView.OnItemSelectedListener {
    ActionBar actionBar;
    private DatagramSocket socket;
    private InetAddress serverAddress;
    private int serverPort;
    private Spinner spinner;

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
        //spinner class for the scroll button
        spinner = (Spinner) findViewById(R.id.fonts_spinner);
        ArrayAdapter<String> adapter = new ArrayAdapter<String>(SecondScreen.this,
                android.R.layout.simple_spinner_item, getResources().getStringArray(R.array.fonts_array));
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinner.setAdapter(adapter);
        spinner.setOnItemSelectedListener(this);

        Button button = findViewById(R.id.button2);
        button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                storeText();
            }
        });
        //recording button
        ToggleButton toggle = (ToggleButton) findViewById(R.id.toggleButton);
        TextView tt = (TextView) findViewById(R.id.toggleButton);
        toggle.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if (isChecked) {
                    startRecording();
                } else {
                    stopRecording();
                }
            }
        });
        //writing button
        ToggleButton togglepart2 = (ToggleButton) findViewById(R.id.toggleButton2);
        TextView ttpart2 = (TextView) findViewById(R.id.toggleButton2);
        togglepart2.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if (isChecked) {
                    startWriting();
                } else {
                    stopWriting();
                }
            }
        });
    }
    //setting up port and IP Address
    private void configureSocket() {
        try {
            this.socket = new DatagramSocket(1068);
            this.serverAddress = InetAddress.getByName("192.168.1.4");                                                                                                                                                                                   this.serverPort = 1069;
        } catch (Exception e) {
            System.out.println(e);
        }
    }
    //function when user picks a text
    public void onItemSelected(AdapterView<?> parent, View view,
                                int pos, long id) {

        String item = parent.getItemAtPosition(pos).toString();
        System.out.println("You have selected the font: " + item );
        storeFont(item);
    }
    //If the user does not pick a font
    public void onNothingSelected(AdapterView<?> parent) {
        // Another interface callback
    }
    
    //listen to receive packets from the server
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
    //processing packets are being received from the server
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

    //sending an ack back
    private void sendMessage(String message) {
        byte[] data = message.getBytes();
        DatagramPacket sendPacket = new DatagramPacket(data, data.length, this.serverAddress, this.serverPort);
        try {
            System.out.println("Sending to " + this.serverAddress + " Port: " + this.serverPort);
            this.socket.send(sendPacket);
        } catch (Exception e) {
            System.out.println(e);
        }
    }

    //methods for commands using opcodes that are recognized by the server
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

    private void storeFont(String item) {
        String opCode = "07";
        sendMessageOnNewThread(opCode + item);
        System.out.println(opCode + " " +  item);
    }
    //Sending message on a new thread
    private void sendMessageOnNewThread(final String message) {
        Thread thread = new Thread(new Runnable() {
            @Override
            public void run() {
                sendMessage(message);
            }
        });
        thread.start();
    }
}
