import { observable, action } from 'mobx';
import reqwest from 'reqwest';

class DocController {
    newDocuments = observable([]);
    documents = [];

    //从后台获取文章，clear 为 true 时会
    getDocuments = action((type = 'all', option = {}, clear = false) => {

        //设置查询开始的 index
        option["start"] = this.newDocuments.length;

        reqwest({
            url: '/api/doclist',
            method: 'get',
            type: 'json',
            data: {
                doc_type: type,
                start_index: this.documents.length === 0 ? null : this.documents[-1]["id"],
                ...option
            }
        })
            .then((data) => {
                console.log(`getDocuments ${data} ${data.errno}`);

                if(data.errno === 0) {

                    //成功时，开始装载新的文章
                    action(() => {
                        if(clear) {
                            this.documents = [];
                            this.newDocuments = [];
                        }

                        for (let doc of data.docs) {
                            console.log(`getDocumentsDoc ${doc}`);
                            this.newDocuments.push(doc)
                        }

                        console.log(this.newDocuments)

                    })();
                }
                else {
                    window.alert(`getDocuments ${data["describe"]}`);
                }
            })
            .fail((err, msg) => {
                console.log(`getGlobalData failed ${err}, ${msg}`);
            })
    });

    //写文章
    writeDocuments = (doc_type, content, hashtag, category, share_url) => {

        console.log("writeDocuments", doc_type, content, hashtag, category, share_url)

        reqwest({
            url: '/api/doc',
            method: 'post',
            type: 'json',
            data: {
                doc_type: doc_type,
                content: content,
                hashtag: hashtag.join(","),
                category: category,
                share_url: share_url,
            }
        })
            .then((data) => {
                console.log(`writeDocuments resp ${data} ${data.errno}`);

                this.clearDocuments();
                this.getDocuments()

            })
            .fail((err, msg) => {
                console.log(`writeDocuments failed ${err}, ${msg}`);
            })
    };

    //修改文章
    editDocuments = (id, content, hashtag) => {

        console.log("editDocuments", id, content, hashtag);

        reqwest({
            url: '/api/doc',
            method: 'patch',
            type: 'json',
            data: {
                id,
                content: content,
                hashtag: hashtag.join(","),
            }
        })
            .then((data) => {
                console.log(`editDocuments resp ${data} ${data.errno}`);

                this.clearDocuments();
                this.getDocuments()

            })
            .fail((err, msg) => {
                console.log(`editDocuments failed ${err}, ${msg}`);
            })
    };

    //清除已 load 文章
    clearDocuments = () => {
        this.documents = [];
        this.newDocuments.splice(0,999);
    }
}

export default new DocController();

