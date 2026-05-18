import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { SubscriptionService } from '../../app_services/subscription.service';

@Component({
  selector: 'app-subscription-success',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="success-container">
      <div class="success-card">
        <div class="success-icon">
          <i class="fa-solid fa-circle-check"></i>
        </div>
        <h1>Welcome to Pro!</h1>
        <p class="success-message">
          Your subscription has been activated successfully.
        </p>
        <div class="benefits">
          <h3>You now have access to:</h3>
          <ul>
            <li><i class="fa-solid fa-check"></i> Unlimited Conversions</li>
            <li><i class="fa-solid fa-check"></i> Larger File Sizes</li>
            <li><i class="fa-solid fa-check"></i> Priority Processing</li>
            <li><i class="fa-solid fa-check"></i> Ad-Free Experience</li>
          </ul>
        </div>
        <button class="cta-button" (click)="goHome()">
          Start Converting
        </button>
      </div>
    </div>
  `,
  styles: [`
    .success-container {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      padding: 2rem;
    }

    .success-card {
      background: white;
      border-radius: 24px;
      padding: 3rem;
      max-width: 500px;
      text-align: center;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }

    .success-icon {
      font-size: 5rem;
      color: #00c853;
      margin-bottom: 1.5rem;
      animation: scaleIn 0.5s ease-out;
    }

    @keyframes scaleIn {
      from {
        transform: scale(0);
      }
      to {
        transform: scale(1);
      }
    }

    h1 {
      font-size: 2.5rem;
      color: #1a202c;
      margin-bottom: 1rem;
    }

    .success-message {
      font-size: 1.1rem;
      color: #718096;
      margin-bottom: 2rem;
    }

    .benefits {
      background: #f7fafc;
      border-radius: 16px;
      padding: 1.5rem;
      margin-bottom: 2rem;
      text-align: left;
    }

    .benefits h3 {
      font-size: 1.1rem;
      color: #2d3748;
      margin-bottom: 1rem;
    }

    .benefits ul {
      list-style: none;
      padding: 0;
      margin: 0;
    }

    .benefits li {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.5rem 0;
      color: #4a5568;
    }

    .benefits i {
      color: #00c853;
      font-size: 1.2rem;
    }

    .cta-button {
      width: 100%;
      padding: 1rem 2rem;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border: none;
      border-radius: 12px;
      font-size: 1.1rem;
      font-weight: 700;
      cursor: pointer;
      transition: transform 0.2s;
    }

    .cta-button:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
    }
  `]
})
export class SubscriptionSuccessComponent implements OnInit {
  isVerifying = true;
  verificationError = false;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private subscriptionService: SubscriptionService
  ) { }

  ngOnInit() {
    // Get session_id from URL query params
    const sessionId = this.route.snapshot.queryParamMap.get('session_id');

    if (sessionId) {
      console.log('Verifying subscription with session_id:', sessionId);

      // Call backend to verify and activate subscription
      this.subscriptionService.verifySubscription(sessionId).subscribe({
        next: (response) => {
          console.log('Subscription verified successfully:', response);
          this.isVerifying = false;

          // Reload subscription status to update UI
          this.subscriptionService.loadSubscriptionStatus();
        },
        error: (error) => {
          console.error('Subscription verification failed:', error);
          this.isVerifying = false;
          this.verificationError = true;
        }
      });
    } else {
      console.warn('No session_id found in URL');
      this.isVerifying = false;

      // Still reload subscription status
      this.subscriptionService.loadSubscriptionStatus();
    }
  }

  goHome() {
    this.router.navigate(['/']);
  }
}
