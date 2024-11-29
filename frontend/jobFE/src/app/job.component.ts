import { Component } from '@angular/core';
import { RouterOutlet, RouterModule} from '@angular/router';
import { DataService } from './data.service';

@Component({
    selector: 'job',
    standalone: true,
    imports: [RouterOutlet, RouterModule],
    providers: [DataService],
    templateUrl: './job.component.html',
    styleUrl: './job.component.css'
})
export class JobComponent {
    job_list: any;
    page: number = 1;
    constructor(public dataService: DataService) { }
    ngOnInit() {
        this.job_list = this.dataService.getJobs(this.page);
    }
    previousPage() {
        if (this.page > 1) {
            this.page = this.page - 1
            this.job_list =
                this.dataService.getJobs(this.page);
        }
    }
    nextPage() {
        if (this.page < this.dataService.getLastPageNumber()) {
        this.page = this.page + 1
        this.job_list =
            this.dataService.getJobs(this.page);
    }
}

}
    
    