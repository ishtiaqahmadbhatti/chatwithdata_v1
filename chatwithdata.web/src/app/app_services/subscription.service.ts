import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';

export interface SubscriptionStatus {
    is_premium: boolean;
    subscription_plan: string; // 'free', 'monthly', 'yearly'
    subscription_status: string; // 'active', 'inactive', 'canceled'
    subscription_expiry: string | null;
}

export interface CheckoutSessionResponse {
    checkout_url: string;
}

@Injectable({
    providedIn: 'root'
})
export class SubscriptionService {
    private apiUrl = 'http://localhost:8000/api/v1';
    private subscriptionStatusSubject = new BehaviorSubject<SubscriptionStatus>({
        is_premium: false,
        subscription_plan: 'free',
        subscription_status: 'inactive',
        subscription_expiry: null
    });

    public subscriptionStatus$ = this.subscriptionStatusSubject.asObservable();

    constructor(private http: HttpClient) {
        this.loadSubscriptionStatus();
    }

    /**
     * Load current user's subscription status
     */
    loadSubscriptionStatus(): void {
        const token = localStorage.getItem('access_token');
        if (!token) {
            return;
        }

        const headers = new HttpHeaders({
            'Authorization': `Bearer ${token}`
        });

        this.http.get<SubscriptionStatus>(`${this.apiUrl}/subscription/status`, { headers })
            .subscribe({
                next: (status) => {
                    this.subscriptionStatusSubject.next(status);
                },
                error: (error) => {
                    console.error('Error loading subscription status:', error);
                }
            });
    }

    /**
     * Create a Stripe checkout session for subscription
     */
    createCheckoutSession(planType: 'monthly' | 'yearly'): Observable<CheckoutSessionResponse> {
        const token = localStorage.getItem('access_token');
        const headers = new HttpHeaders({
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        });

        return this.http.post<CheckoutSessionResponse>(
            `${this.apiUrl}/payments/create-checkout-session`,
            { plan_type: planType },
            { headers }
        ).pipe(
            tap(response => {
                // Redirect to Stripe checkout
                if (response.checkout_url) {
                    window.location.href = response.checkout_url;
                }
            })
        );
    }

    /**
     * Verify and activate subscription using Stripe session ID
     */
    verifySubscription(sessionId: string): Observable<any> {
        const token = localStorage.getItem('access_token');
        const headers = new HttpHeaders({
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        });

        return this.http.post(
            `${this.apiUrl}/payments/verify-session`,
            { session_id: sessionId },
            { headers }
        );
    }

    /**
     * Get current subscription status
     */
    getCurrentStatus(): SubscriptionStatus {
        return this.subscriptionStatusSubject.value;
    }

    /**
     * Check if user is premium
     */
    isPremium(): boolean {
        return this.subscriptionStatusSubject.value.is_premium;
    }

    /**
     * Get current plan type
     */
    getCurrentPlan(): string {
        return this.subscriptionStatusSubject.value.subscription_plan;
    }
}
