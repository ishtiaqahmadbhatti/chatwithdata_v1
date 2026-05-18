import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FileConversionUiComponent } from '../../../../app_shared/file-conversion-ui/file-conversion-ui.component';
import { BaseXmlToolComponent } from '../base-xml-tool.component';

@Component({
  selector: 'app-excel-to-xml',
  imports: [CommonModule, FormsModule, FileConversionUiComponent],
  templateUrl: './excel-to-xml.component.html',
  styleUrl: './excel-to-xml.component.css',
  standalone: true
})
export class ExcelToXmlComponent extends BaseXmlToolComponent {
  toolId = 'excel-to-xml';
}
