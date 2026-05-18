import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseXmlToolComponent } from '../base-xml-tool.component';

@Component({
  selector: 'app-fix-xml-escaping',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './fix-xml-escaping.component.html',
  styleUrl: './fix-xml-escaping.component.css',
  standalone: true
})
export class FixXmlEscapingComponent extends BaseXmlToolComponent {
  toolId = 'fix-xml-escaping';
}
