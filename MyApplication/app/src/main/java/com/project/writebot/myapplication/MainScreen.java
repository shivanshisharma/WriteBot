package com.project.writebot.myapplication;

import android.content.Intent;
import android.graphics.Color;
import android.graphics.drawable.ColorDrawable;
import android.support.v7.app.ActionBar;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

public class MainScreen extends AppCompatActivity {
    ActionBar actionBar;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main_screen); 

        Button button = findViewById(R.id.button);
        button.setOnClickListener(new View.OnClickListener() //for the button on main screen {
            @Override
            public void onClick(View v) { //setting what the button should do next
                Intent intent = new Intent(MainScreen.this, SecondScreen.class);
                startActivity(intent);
            }
        });

        actionBar = getSupportActionBar();
        actionBar.setBackgroundDrawable(new ColorDrawable(Color.parseColor("#FF000000")));
    }
}
