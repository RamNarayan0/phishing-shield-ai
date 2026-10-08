package com.phishingshield;

import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;
import android.util.Log;
import org.json.JSONObject;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

public class PhishingShieldListenerService extends NotificationListenerService {
    private static final String TAG = "PhishingShield";
    // Replace with actual LAN or cloud backend IP
    private static final String API_URL = "http://10.0.2.2:8000/api/events"; 

    @Override
    public void onNotificationPosted(StatusBarNotification sbn) {
        String packageName = sbn.getPackageName();
        CharSequence text = sbn.getNotification().extras.getCharSequence("android.text");
        
        if (text != null && !packageName.equals("com.phishingshield")) {
            sendToBackend(packageName, text.toString());
        }
    }

    private void sendToBackend(String appName, String rawText) {
        new Thread(() -> {
            try {
                URL url = new URL(API_URL);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setRequestProperty("Content-Type", "application/json");
                conn.setDoOutput(true);

                JSONObject json = new JSONObject();
                json.put("raw_text", rawText);
                json.put("source_platform", "Android Notification");
                json.put("application_name", appName);

                try(OutputStream os = conn.getOutputStream()) {
                    byte[] input = json.toString().getBytes("utf-8");
                    os.write(input, 0, input.length);
                }

                int code = conn.getResponseCode();
                Log.d(TAG, "Sent to backend. Response: " + code);
            } catch (Exception e) {
                Log.e(TAG, "Failed to send notification to backend", e);
            }
        }).start();
    }
}
