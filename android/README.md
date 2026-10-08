# Phishing Shield AI - Android Client

This is the scaffold for the Android application component of Phishing Shield AI.

## Architecture

The Android app integrates with the core backend using a `NotificationListenerService`.

```
Android notification
        ↓
NotificationListenerService
        ↓
Extract notification text
        ↓
POST /api/verify-message
        ↓
Risk score
        ↓
Android Alert (Toast or Local Notification)
```

## Next Implementation Steps

To complete this component:
1. Create a new Android Studio project.
2. Add a service extending `NotificationListenerService`.
3. Request `BIND_NOTIFICATION_LISTENER_SERVICE` permission in `AndroidManifest.xml`.
4. Prompt the user to grant Notification Access in Android settings.
5. In `onNotificationPosted`, extract the text from the `StatusBarNotification` payload.
6. Use Retrofit or OkHttp to POST the extracted text to `http://<backend-ip>:8000/api/verify-message`.
7. Display an alert overlay if the verdict is `CRITICAL` or `HIGH RISK`.

Note: This component is deferred to prioritize the stability of the core Python backend, React frontend, and Chrome Extension prototype.
