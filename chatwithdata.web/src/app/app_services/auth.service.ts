import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { Router } from '@angular/router';
import { ApplicationConfiguration } from '../app.config';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl: string;
  private readonly TOKEN_KEY = 'access_token';
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';
  private readonly USER_NAME_KEY = 'user_name';
  private readonly USER_EMAIL_KEY = 'user_email';
  private readonly USER_IMAGE_KEY = 'user_image';

  private authUrl: string;

  private isLoggedInSubject = new BehaviorSubject<boolean>(this.hasToken());
  public isLoggedIn$ = this.isLoggedInSubject.asObservable();

  private profileImageSubject = new BehaviorSubject<string | null>(null);
  public profileImage$ = this.profileImageSubject.asObservable();

  constructor(private http: HttpClient, private router: Router) {
    this.apiUrl = ApplicationConfiguration.Get().ApiServiceLink;
    this.authUrl = `${this.apiUrl}/auth`;

    // Load profile image from localStorage if available
    const savedImage = this.getUserProfileImage();
    if (savedImage) {
      this.profileImageSubject.next(savedImage);
    }
  }

  private hasToken(): boolean {
    if (typeof localStorage !== 'undefined') {
      return !!localStorage.getItem(this.TOKEN_KEY);
    }
    return false;
  }

  register(userData: any): Observable<any> {
    const url = `${this.authUrl}/register-userlist`;
    return this.http.post(url, userData);
  }

  login(credentials: { email: string, password: string }): Observable<any> {
    const url = `${this.authUrl}/login-userlist`;
    return this.http.post(url, credentials);
  }

  changePassword(passwords: { old_password: string, new_password: string }): Observable<any> {
    const url = `${this.authUrl}/change-password`;
    return this.http.post(url, passwords);
  }

  sendOtp(email: string, deviceId: string): Observable<any> {
    const url = `${this.authUrl}/forgot-password`;
    return this.http.post(url, { email, device_id: deviceId });
  }

  verifyOtp(email: string, otp: string): Observable<any> {
    const url = `${this.authUrl}/verify-otp`;
    return this.http.post(url, { email, otp_code: otp });
  }

  resetPassword(data: { reset_token: string, new_password: string }): Observable<any> {
    const url = `${this.authUrl}/reset-password-confirm`;
    return this.http.post(url, data);
  }

  updateProfile(data: any): Observable<any> {
    const url = `${this.authUrl}/update-profile`;
    return this.http.put(url, data);
  }

  uploadProfileImage(file: File): Observable<any> {
    const url = `${this.authUrl}/upload-profile-image`;
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(url, formData);
  }

  getSubscriptionStatus(): Observable<any> {
    const url = `${this.apiUrl}/subscription/status`;
    return this.http.get(url);
  }

  upgradeSubscription(planId: string, paymentMethodId?: string): Observable<any> {
    const url = `${this.apiUrl}/subscription/upgrade`;
    return this.http.post(url, { plan_id: planId, payment_method_id: paymentMethodId });
  }

  getUserProfile(): Observable<any> {
    const url = `${this.authUrl}/me`;
    return this.http.get(url);
  }

  saveTokens(access: string, refresh: string, name?: string, email?: string, image?: string): void {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(this.TOKEN_KEY, access);
      localStorage.setItem(this.REFRESH_TOKEN_KEY, refresh);
      if (name) localStorage.setItem(this.USER_NAME_KEY, name);
      if (email) localStorage.setItem(this.USER_EMAIL_KEY, email);
      if (image) {
        localStorage.setItem(this.USER_IMAGE_KEY, image);
        this.profileImageSubject.next(image);
      }
      this.isLoggedInSubject.next(true);
    }
  }

  getToken(): string | null {
    if (typeof localStorage !== 'undefined') {
      return localStorage.getItem(this.TOKEN_KEY);
    }
    return null;
  }

  getUserName(): string | null {
    if (typeof localStorage !== 'undefined') {
      return localStorage.getItem(this.USER_NAME_KEY);
    }
    return null;
  }

  getUserEmail(): string | null {
    if (typeof localStorage !== 'undefined') {
      return localStorage.getItem(this.USER_EMAIL_KEY);
    }
    return null;
  }

  getUserProfileImage(): string | null {
    if (typeof localStorage !== 'undefined') {
      return localStorage.getItem(this.USER_IMAGE_KEY);
    }
    return null;
  }

  updateProfileImage(url: string): void {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(this.USER_IMAGE_KEY, url);
      this.profileImageSubject.next(url);
    }
  }

  getUserInitials(): string {
    const name = this.getUserName();
    if (!name) return 'U';

    const parts = name.trim().split(' ');
    if (parts.length === 1) {
      return parts[0].substring(0, 2).toUpperCase();
    }
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }

  logout(): void {
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem(this.TOKEN_KEY);
      localStorage.removeItem(this.REFRESH_TOKEN_KEY);
      localStorage.removeItem(this.USER_NAME_KEY);
      localStorage.removeItem(this.USER_EMAIL_KEY);
      localStorage.removeItem(this.USER_IMAGE_KEY);
      this.isLoggedInSubject.next(false);
      this.profileImageSubject.next(null);
    }
    this.router.navigate(['/']);
  }

  registerGuest(): Observable<any> {
    const deviceId = this.getDeviceId();
    const url = `${this.apiUrl}/guest/register`;
    return this.http.post(url, { device_id: deviceId });
  }

  getDeviceId(): string {
    if (typeof window !== 'undefined' && typeof navigator !== 'undefined') {
      const fingerprint = this.generateDeviceFingerprint();
      // Cache it
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('device_id', fingerprint);
      }
      return fingerprint;
    }
    return 'unknown-device';
  }

  private generateDeviceFingerprint(): string {
    const nav = window.navigator as any;
    const screen = window.screen;

    // Device components that are generally consistent across browsers on the same device
    const components = [
      // nav.language, // REMOVED: User preference can vary (e.g. en-US vs en-GB)
      screen.colorDepth,
      screen.width + 'x' + screen.height,
      Intl.DateTimeFormat().resolvedOptions().timeZone,
      nav.hardwareConcurrency,
      // nav.deviceMemory, // REMOVED: Not supported in all browsers
      nav.platform,
      nav.maxTouchPoints || 0 // Good signal for touch devices
    ];

    // Create a unique string from consistent components
    // We treat undefined deviceMemory as a consistent 'undefined' string for non-Chromium browsers
    // Note: This means Chrome and Firefox on the SAME machine might still differ if one has deviceMemory and other doesn't.
    // To fix that, we can either exclude deviceMemory or just accept that cross-engine (Gecko vs Blink) might differ,
    // but Chrome vs Edge (both Blink) will match. The user specifically mentioned Chrome vs Edge (both Blink).
    const rawString = components.join('||');

    // Log for debugging (so you can see why they differ if they still do)
    console.log('Device Fingerprint Components:', rawString);

    // Generate Hash
    const hash = this.simpleHash(rawString);

    // Determine Platform/Device Type for readability (using UA is fine here as it's just a label prefix, not the hash source)
    let deviceType = 'Desktop';
    const ua = nav.userAgent.toLowerCase();
    if (/mobile|android|iphone|ipad|ipod|windows phone/i.test(ua)) {
      deviceType = 'Mobile';
    } else if (/tablet|ipad/i.test(ua)) {
      deviceType = 'Tablet';
    }

    let os = 'UnknownOS';
    if (ua.indexOf('win') !== -1) os = 'Windows';
    else if (ua.indexOf('mac') !== -1) os = 'MacOS';
    else if (ua.indexOf('linux') !== -1) os = 'Linux';
    else if (ua.indexOf('android') !== -1) os = 'Android';
    else if (ua.indexOf('ios') !== -1) os = 'iOS';

    // Format: Platform-OS-Hash (e.g., Mobile-Android-a1b2c3d4)
    return `${deviceType}-${os}-${hash}`;
  }

  private simpleHash(str: string): string {
    let hash = 0;
    if (str.length === 0) return hash.toString();
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    // Return positive hex string
    return Math.abs(hash).toString(16);
  }

  isLoggedIn(): boolean {
    return this.isLoggedInSubject.value; // Use the subject's current value for synchronous check
  }
}
