import ReactTable from "react-table";
import "react-table/react-table.css";

import React from "react";

import axios from "axios";

const HEAD_URL = "http://localhost:5000/";

function FileUploadProgress(props) {
  if (props.completed == 0 && props.total == 0) {
    return <h1>No Upload in progress</h1>;
  } else {
    return (
      <h1>
        Completed: {props.completed} Total {props.total}
      </h1>
    );
  }
}

function Greeting(props) {
  const total = props.total;
  const completed = props.completed;
  return <FileUploadProgress total={total} completed={completed} />;
}

//function to sort the results
function filterCaseInsensitive(filter, row) {
  const id = filter.pivotId || filter.id;
  return row[id] !== undefined
    ? String(row[id].toLowerCase()).startsWith(filter.value.toLowerCase())
    : true;
}

export default class ProductList extends React.Component {
  state = {
    products: [],
    selectedFile: null,
    total: 0,
    completed: 0
  };

  constructor(props) {
    super(props);
    this.eventSource = new EventSource(HEAD_URL + "events");
  }

  update_product_list() {
    axios.get(HEAD_URL + "product").then(res => {
      const products = res.data;
      this.setState({ products });
    });
  }

  update_product_event_message(e) {
    let obj = JSON.parse(e.data);
    this.setState({
      total: obj.total,
      completed: obj.completed
    });
    if (obj.total > 0 && obj.completed > 0 && obj.completed == obj.total) {
      this.update_product_list();
      this.setState({
        total: 0,
        completed: 0
      });
    }
  }

  componentDidMount() {
    this.setState({
      products: [],
      selectedFile: null,
      total: 0,
      completed: 0
    });
    this.update_product_list();
    this.eventSource.onmessage = e => this.update_product_event_message(e);
  }

  onChangeHandler = event => {
    this.setState({
      selectedFile: event.target.files[0],
      loaded: 0
    });
  };

  onUploadClickHandler = () => {
    const data = new FormData();
    this.setState({
      // fileUploading: true
    });
    data.append("file", this.state.selectedFile);
    axios.post(HEAD_URL + "product", data, {}).then(res => {
      // then print response status
      this.setState({
        // fileUploading: false
      });
      this.update_product_list();
    });
  };

  onDeleteClickHandler = () => {
    axios
      .delete(HEAD_URL + "product", {
        // receive two    parameter endpoint url ,form data
      })
      .then(res => {
        // then print response status
        // console.log(res.statusText)
        this.update_product_list();
      });
  };

  // renderEditable(cellInfo) {
  //   return (
  //     <div
  //       style={{ backgroundColor: "#fafafa" }}
  //       contentEditable
  //       suppressContentEditableWarning
  //       onBlur={e => {
  //         const data = [...this.state.data];
  //         data[cellInfo.index][cellInfo.column.id] = e.target.innerHTML;
  //         this.setState({ data });
  //       }}
  //       dangerouslySetInnerHTML={{
  //         __html: this.state.data[cellInfo.index][cellInfo.column.id]
  //       }}
  //     />
  //   );
  //  }

  render() {
    const columns = [
      {
        Header: "SKU",
        accessor: "sku"
      },
      {
        Header: "Name",
        accessor: "name"
        // Cell: this.renderEditable
      },
      {
        Header: "Description",
        accessor: "description"
        // Cell: this.renderEditable
      }
    ];
    return (
      <div>
        <div>
          <ReactTable
            filterable
            defaultFilterMethod={(filter, row) =>
              filterCaseInsensitive(filter, row)
            }
            data={this.state.products}
            columns={columns}
            defaultPageSize={10}
            pageSizeOptions={[10, 25, 50, 100, 200]}
          />
        </div>
        <div>
          <input type="file" name="file" onChange={this.onChangeHandler} />
          <button
            type="button"
            className="btn btn-success btn-block"
            onClick={this.onUploadClickHandler}
          >
            Upload
          </button>
          <button
            type="button"
            className="btn btn-error btn-block"
            onClick={this.onDeleteClickHandler}
          >
            Delete All
          </button>
          <div>
            <Greeting
              fileUploading={this.state.fileUploading}
              total={this.state.total}
              completed={this.state.completed}
            />
          </div>
        </div>
      </div>
    );
  }
}
