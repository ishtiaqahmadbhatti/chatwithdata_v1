import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
    selector: 'app-subscription-cancel',
    standalone: true,
    imports: [CommonModule],
    template: `
    <div class="cancel-container">
      <div class="cancel-card">
        <div class="cancel-icon">
          <i class="fa-solid fa-circle-xmark"></i>
        </div>
        <h1>Subscription Cancelled</h1>
        <p class="cancel-message">
          Your subscription process was cancelled. No charges were made.
        </p>
        <p class="help-text">
          If you encountered any issues or have questions, please contact our support team.
        </p>
        <div class="button-group">
          <button class="primary-button" (click)="goToPricing()">
            View Plans Again
          </button>
          <button class="secondary-button" (click)="goHome()">
            Go to Home
          </button>
        </div>
      </div>
    </div>
  `,
    styles: [`
    .cancel-container {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      padding: 2rem;
    }

    .cancel-card {
      background: white;
      border-radius: 24px;
      padding: 3rem;
      max-width: 500px;
      text-align: center;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }

    .cancel-icon {
      font-size: 5rem;
      color: #f56565;
      margin-bottom: 1.5rem;
    }

    h1 {
      font-size: 2.5rem;
      color: #1a202c;
      margin-bottom: 1rem;
    }

    .cancel-message {
      font-size: 1.1rem;
      color: #718096;
      margin-bottom: 1rem;
    }

    .help-text {
      font-size: 0.95rem;
      color: #a0aec0;
      margin-bottom: 2rem;
    }

    .button-group {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .primary-button, .secondary-button {
      width: 100%;
      padding: 1rem 2rem;
      border: none;
      border-radius: 12px;
      font-size: 1.1rem;
      font-weight: 700;
      cursor: pointer;
      transition: transform 0.2s;
    }

    .primary-button {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }

    .secondary-button {
      background: transparent;
      color: #667eea;
      border: 2px solid #667eea;
    }

    .primary-button:hover, .secondary-button:hover {
      transform: translateY(-2px);
    }
  `]
})
export class SubscriptionCancelComponent {
    constructor(private router: Router) { }

    goToPricing() {
        this.router.navigate(['/pricing']);
    }

    goHome() {
        this.router.navigate(['/']);
    }
}
