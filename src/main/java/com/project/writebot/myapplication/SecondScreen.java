package com.project.writebot.myapplication;

import android.content.Intent;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.app.ActionBar;
import android.view.View;
import android.widget.Button;
import android.widget.CompoundButton;
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
        try {
            this.socket = new DatagramSocket(1068);
            this.serverAddress = InetAddress.getByName("134.117.57.194");
            this.serverPort = 1069;
        } catch(Exception e) {
            System.out.println(e);
        }
        actionBar = getSupportActionBar();
        actionBar.setBackgroundDrawable(new ColorDrawable(Color.parseColor("#FF000000")));

        Button button = findViewById(R.id.button2);
        button.setOnClickListener(new View.OnClickListener() {

            @Override
            public void onClick(View v) {
                Thread thread = new Thread(new Runnable() {
                    @Override
                    public void run() {
                        try  {
                            storeText();
                            System.out.println("sendtextworks");
                        } catch (Exception e) {
                            e.printStackTrace();
                        }
                    }
                });
                thread.start();
            }
        });
        ToggleButton toggle = (ToggleButton) findViewById(R.id.toggleButton);
        TextView tt = (TextView) findViewById(R.id.toggleButton);
        toggle.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if(isChecked){
                    Thread thread = new Thread(new Runnable() {
                        @Override
                        public void run() {
                            try  {
                                startRecording();
                                System.out.println("startworks");
                            } catch (Exception e) {
                                e.printStackTrace();
                            }
                        }
                    });
                    thread.start();
                }
                else{
                    Thread thread = new Thread(new Runnable() {
                        @Override
                        public void run() {
                            try  {
                                stopRecording();
                                System.out.println("stopworks");
                            } catch (Exception e) {
                                e.printStackTrace();
                            }
                        }
                    });
                    thread.start();
                }
            }
        });
        ToggleButton togglepart2 = (ToggleButton) findViewById(R.id.toggleButton2);
        TextView ttpart2 = (TextView) findViewById(R.id.toggleButton2);
        togglepart2.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if(isChecked){
                    Thread thread = new Thread(new Runnable() {
                        @Override
                        public void run() {
                            try  {
                                startWriting();
                                System.out.println("startwriteworks");
                            } catch (Exception e) {
                                e.printStackTrace();
                            }
                        }
                    });
                    thread.start();
                }
                else{
                    Thread thread = new Thread(new Runnable() {
                        @Override
                        public void run() {
                            try  {
                                stopWriting();
                                System.out.println("stopwriteworks");
                            } catch (Exception e) {
                                e.printStackTrace();
                            }
                        }
                    });
                    thread.start();
                }
            }
        });
    }

    private void startRecording() {
        String opCode = "01";
        sendMessage(opCode);
    }

    private void stopRecording() {
        String opCode = "02";
        sendMessage(opCode);
    }

    private void storeText() {
        TextView textView = findViewById(R.id.editText);
        String newText = textView.getText().toString();
        String opCode = "03";
        sendMessage(opCode + newText);
    }

    private void startWriting() {
        String opCode = "04";
        sendMessage(opCode);
    }

    private void stopWriting() {
        String opCode = "05";
        sendMessage(opCode);
    }

    private void sendMessage(String message) {
        byte[] data = message.getBytes();
        DatagramPacket sendPacket = new DatagramPacket(data, data.length, this.serverAddress, this.serverPort);
        try {
            this.socket.send(sendPacket);
        } catch(Exception e) {
            System.out.println(e);
        }
    }
}
