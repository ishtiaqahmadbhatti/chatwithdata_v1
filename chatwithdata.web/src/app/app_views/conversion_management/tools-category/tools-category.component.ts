import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ToolCategory } from '../../../app_models/tool-category.model';
import { TOOLS_CATEGORIES } from '../../../app_data/tools-category.data';

@Component({
  selector: 'app-tools-category',
  templateUrl: './tools-category.component.html',
  styleUrls: ['./tools-category.component.css'],
  standalone: true,
  imports: [CommonModule, RouterLink]
})
export class ToolsCategoryComponent {
  categories: ToolCategory[] = TOOLS_CATEGORIES;
}
