import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PRICING_DATA } from '../../app_data/pricing.data';
import { AuthService } from '../../app_services/auth.service';
import { SubscriptionService } from '../../app_services/subscription.service';
import { Router } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';

@Component({
    selector: 'app-pricing',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './pricing.component.html',
    styleUrls: ['./pricing.component.css']
})
export class PricingComponent implements OnInit, OnDestroy {
    plans = PRICING_DATA;
    currentPlanId = 'free';
    processingPlanId: string | null = null;  // Track which plan is being processed
    private destroy$ = new Subject<void>();

    constructor(
        public authService: AuthService,
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

    selectPlan(plan: any) {
        // Free plan doesn't need any action
        if (plan.planId === 'free') {
            return;
        }

        // Check if user is logged in
        const token = localStorage.getItem('access_token');
        if (!token) {
            alert('Please sign in to view subscription options');
            this.router.navigate(['/authentication/signin']);
            return;
        }

        // Redirect to subscription page for actual upgrade
        this.router.navigate(['/profile/subscription']);
    }

    getButtonText(plan: any): string {
        if (plan.planId === this.currentPlanId) {
            return 'Current Plan';
        }
        if (plan.planId === 'monthly' || plan.planId === 'yearly') {
            return 'Coming Soon';
        }
        return plan.buttonText;
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
