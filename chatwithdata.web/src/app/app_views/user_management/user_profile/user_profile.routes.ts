import { Routes } from '@angular/router';

export const ProfileRoutes: Routes = [
  {
    path: 'personal-info',
    loadComponent: () => import('./user-profile-update/user-profile-update.component').then(c => c.UserProfileUpdateComponent)
  },
  {
    path: 'change-password',
    loadComponent: () => import('../user_authentication/changepassword/changepassword.component').then(c => c.ChangepasswordComponent)
  },
  {
    path: 'subscription',
    loadComponent: () => import('./subscription/subscription.component').then(c => c.SubscriptionComponent)
  },
  {
    path: 'deleteprofile',
    loadComponent: () => import('./user-profile-delete/user-profile-delete.component').then(c => c.UserProfileDeleteComponent)
  },
  // Maintain old route for backward compatibility if needed, else remove
  {
    path: 'updateprofile',
    redirectTo: 'personal-info',
    pathMatch: 'full'
  }
];