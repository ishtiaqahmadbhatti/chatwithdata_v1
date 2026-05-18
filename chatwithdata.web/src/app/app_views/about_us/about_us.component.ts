import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ABOUT_US_DATA } from '../../app_data/about-us.data';

@Component({
    selector: 'app-about-us',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './about_us.component.html',
    styleUrls: ['./about_us.component.css']
})
export class AboutUsComponent {
    data = ABOUT_US_DATA;
    currentYear = new Date().getFullYear();

    // Helper to toggle feature accordion if needed, OR just list them out. 
    // Mobile uses ExpansionTile. We can implement a simple accordion or just show them.
    // Let's implement a simple accordion state.
    openCategoryIndex: number | null = null;

    toggleCategory(index: number) {
        if (this.openCategoryIndex === index) {
            this.openCategoryIndex = null;
        } else {
            this.openCategoryIndex = index;
        }
    }
}
