import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../../app_services/auth.service';
import { SubscriptionService } from '../../../../app_services/subscription.service';
import { Router } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';
import { PRICING_DATA } from '../../../../app_data/pricing.data';

@Component({
    selector: 'app-subscription',
    templateUrl: './subscription.component.html',
    styleUrl: './subscription.component.css',
    standalone: true,
    imports: [CommonModule]
})
export class SubscriptionComponent implements OnInit, OnDestroy {
    currentPlanId = 'free';
    processingPlanId: string | null = null;
    plans = PRICING_DATA;
    private destroy$ = new Subject<void>();

    constructor(
        private authService: AuthService,
        private subscriptionService: SubscriptionService,
        private router: Router
    ) { }

    ngOnInit() {
        // Subscribe to subscription status changes
        this.subscriptionService.subscriptionStatus$
            .pipe(takeUntil(this.destroy$))
            .subscribe(status => {
                if (status) {
                    this.currentPlanId = status.subscription_plan || 'free';
                }
            });

        // Load initial subscription status
        this.subscriptionService.loadSubscriptionStatus();
    }

    ngOnDestroy() {
        this.destroy$.next();
        this.destroy$.complete();
    }

    upgradePlan(plan: any) {
        // Free plan doesn't need any action
        if (plan.planId === 'free') {
            return;
        }

        // Already on this plan
        if (this.currentPlanId === plan.planId) {
            return;
        }

        // Prevent double clicks
        if (this.processingPlanId) {
            return;
        }

        this.processingPlanId = plan.planId;

        // Create Stripe checkout session
        const planType = plan.stripePlanType as 'monthly' | 'yearly';
        this.subscriptionService.createCheckoutSession(planType)
            .subscribe({
                next: (response) => {
                    // User will be redirected to Stripe checkout
                    console.log('Redirecting to Stripe checkout...');
                },
                error: (error) => {
                    console.error('Error creating checkout session:', error);
                    this.processingPlanId = null;

                    if (error.status === 401) {
                        alert('Your session has expired. Please sign in again.');
                        this.router.navigate(['/authentication/signin']);
                    } else {
                        alert('Failed to start checkout. Please try again.');
                    }
                }
            });
    }

    getButtonText(plan: any): string {
        if (plan.planId === this.currentPlanId) {
            return 'Current Plan';
        }
        if (plan.planId === 'monthly' || plan.planId === 'yearly') {
            return 'Coming Soon';
        }
        return 'Upgrade Now';
    }

    isCurrentPlan(planId: string): boolean {
        return this.currentPlanId === planId;
    }

    isButtonDisabled(plan: any): boolean {
        // All buttons disabled as per requirement
        return true;
    }

    isProcessingPlan(planId: string): boolean {
        return this.processingPlanId === planId;
    }
}
