import jsonData from '../assets/Job_vacancies.json'
export class DataService {
    pageSize: number = 3;
    getJobs(page: number) {
        let pageStart = (page - 1) * this.pageSize;
        let pageEnd = pageStart + this.pageSize;
        return jsonData.slice(pageStart, pageEnd);
}
    getLastPageNumber() {
        return Math.ceil( jsonData.length / this.pageSize );
    }
    getjob(id: any) {
        let dataToReturn: any[] = [];
        jsonData.forEach( function(job) {
            if (job['_id']['$oid'] == id) {
                dataToReturn.push( job );
            }
        })
        return dataToReturn;
    }
}