import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PRIVACY_POLICY_DATA } from '../../app_data/privacy-policy.data';

@Component({
    selector: 'app-privacy-policy',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './privacy_policy.component.html',
    styleUrls: ['./privacy_policy.component.css']
})
export class PrivacyPolicyComponent {
    currentYear = new Date().getFullYear();

    sections = PRIVACY_POLICY_DATA;
}
