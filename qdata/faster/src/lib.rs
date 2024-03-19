use pyo3::prelude::*;
use numpy::PyReadonlyArray1;


/*
Reference Python Code:
def id_dt_conv_process(stock_name: str, datetime: str) -> tuple[str, str]:
    if len(datetime) > 10:
        datetime = datetime[:10]
    datetime = datetime[:4] + datetime[5:7] + datetime[8:10]
    stock_name = stock_name.zfill(6)
    key = f'{stock_name}_{datetime}'
    hash_ = stock_name[:4]
    return hash_, key
*/
#[pyfunction]
fn id_dt_conv_process(stock_name: &str, datetime: &str) -> PyResult<(String, String)> {
    let datetime = if datetime.len() > 10 {
        &datetime[..10]
    } else {
        datetime
    };
    let datetime = format!("{}{}{}", &datetime[..4], &datetime[5..7], &datetime[8..10]);
    let stock_name = format!("{:0>6}", stock_name);
    let key = format!("{}_{}", stock_name, datetime);
    let hash_ = stock_name[..4].to_string();
    Ok((hash_, key))
}


/*
Reference Python Code:
def flt_kv_s_process(stock_name: str, datetime: str, key_map: np.array):
    datetime = int(datetime[:4] + datetime[5:7] + datetime[8:10])
    return f'{stock_name}_{datetime}'
*/

#[pyfunction]
fn flt_kv_s_process(stock_name: &str, datetime: &str, key_map: PyReadonlyArray1<u16>) -> PyResult<String> {
    let datetime = format!("{}{}{}", &datetime[..4], &datetime[5..7], &datetime[8..10]);
    let datetime: u32 = datetime.parse().unwrap();
    let r = format!("{}_{}", stock_name, datetime);
    let _key_map = key_map.as_array();
    Ok(r)
}

/*
Reference Python Code:
def flt_kv_process(stock_name: str, start_datetime: str, end_datetime: str, key_map: np.array) -> List[str]:
    start_datetime = int(start_datetime[:4] + start_datetime[5:7] + start_datetime[8:10])
    end_datetime = int(end_datetime[:4] + end_datetime[5:7] + end_datetime[8:10])

    start_idx = key_map.searchsorted(start_datetime, side='left')
    for i in range(start_idx, len(key_map)):
        if key_map[i] > end_datetime:
            ret = key_map[start_idx:i]
            break
    else:
        ret = key_map[start_idx:]
    return list(map(lambda x: f'{stock_name}_{x}', ret))
*/

#[pyfunction]
fn flt_kv_process(stock_name: &str, start_datetime: &str, end_datetime: &str, key_map: PyReadonlyArray1<u32>) -> PyResult<Vec<String>> {
    let start_datetime = format!("{}{}{}", &start_datetime[..4], &start_datetime[5..7], &start_datetime[8..10]);
    let start_datetime: u32 = start_datetime.parse().unwrap();
    let end_datetime = format!("{}{}{}", &end_datetime[..4], &end_datetime[5..7], &end_datetime[8..10]);
    let end_datetime: u32 = end_datetime.parse().unwrap();
    let key_map = key_map.as_array();
    let mut start_idx = 0;
    for (i, &x) in key_map.iter().enumerate() {
        if x > start_datetime {
            start_idx = i;
            break;
        }
    }
    let mut ret = Vec::new();
    for (i, &x) in key_map.iter().enumerate().skip(start_idx) {
        if x > end_datetime {
            // ret = key_map[start_idx..i].iter().map(|x| format!("{}_{}", stock_name, x)).collect();
            break;
        }
    }
    if ret.is_empty() {
        // ret = key_map[start_idx..].iter().map(|x| format!("{}_{}", stock_name, x)).collect();
    }
    Ok(ret)
}


/*
Reference Python Code:
def np_post_flt_process(r_data: List[bytes], fields: Optional[List[str]], frequency: str, adjust: int, limit: int, raw: bool=False) -> bytes:
    if raw:
        return b''.join(r_data)
    stacked = np.hstack(tuple(map(lambda x: np.frombuffer(x, dtype=PL_DTYPE, ), r_data)))
    if frequency == '5m':
        # 5分钟频率
        stacked = stacked[::5]
    return stacked.tobytes()
*/

#[pyfunction]
fn np_post_flt_process(r_data: Vec<&[u8]>, fields: Vec<String>, frequency: &str, adjust: i32, limit: i32, raw: bool) -> PyResult<Vec<f64>> {
    if raw {
        let mut ret = Vec::new();
        for &x in r_data.iter() {
            ret.extend_from_slice(x);
        }
        // convert ret
        // ret = ret.iter().map(|x| unsafe { std::mem::transmute::<u8, f64>(*x) }).collect();
        // return Ok(ret);
    }
    let mut stacked = Vec::new();
    for &x in r_data.iter() {
        let x = unsafe { std::slice::from_raw_parts(x.as_ptr() as *const f64, x.len() / 8) };
        stacked.extend_from_slice(x);
    }
    if frequency == "5m" {
        // 5分钟频率
        stacked = stacked.iter().step_by(5).cloned().collect();
    }
    Ok(stacked)
}

/*
Reference Python Code:
def np_post_flt_s_process(r_data: bytes, datetime: str, fields: Optional[List[str]], frequency: str, adjust: int, raw: bool=True) -> bytes:
    if not raw:
        raise NotImplementedError()
    try:
        time_str = datetime[11:13]+datetime[14:16]+datetime[17:]
        while time_str[0] == '0':
            time_str = time_str[1:]
        else:
            time_str = int(time_str)
        t_idx = TIME_DICT.index(time_str)
    except:
        t_idx = 0
    PL_DTYPE_itemsize = 28
    return r_data[t_idx * PL_DTYPE_itemsize: (t_idx+1)*PL_DTYPE_itemsize]
*/
#[pyfunction]
fn np_post_flt_s_process(r_data: &[u8], datetime: &str, fields: Vec<String>, frequency: &str, adjust: i32, raw: bool) -> PyResult<Vec<f64>> {
    if !raw {
        // return Err(PyErr::new::<NotImplementedError, _>("NotImplementedError"));
    }
    let time_str = format!("{}{}{}", &datetime[11..13], &datetime[14..16], &datetime[17..]);
    let time_str = time_str.trim_start_matches('0').parse::<u32>().unwrap();
    let t_idx = 0;
    let PL_DTYPE_itemsize = 28;
    let r_data = &r_data[t_idx * PL_DTYPE_itemsize..(t_idx + 1) * PL_DTYPE_itemsize];
    let r_data = unsafe { std::slice::from_raw_parts(r_data.as_ptr() as *const f64, r_data.len() / 8) };
    Ok(r_data.to_vec())
}



#[pyfunction]
fn process_numpy_array(numpy_array: PyReadonlyArray1<f64>) -> PyResult<usize> {
    let numpy_array = numpy_array.as_array();
    let r: usize = numpy_array.len();
    Ok(r)
}


/// A Python module implemented in Rust.
#[pymodule]
fn fib_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(id_dt_conv_process, m)?)?;
    m.add_function(wrap_pyfunction!(flt_kv_process, m)?)?;
    m.add_function(wrap_pyfunction!(flt_kv_s_process, m)?)?;
    m.add_function(wrap_pyfunction!(np_post_flt_process, m)?)?;
    m.add_function(wrap_pyfunction!(np_post_flt_s_process, m)?)?;
    m.add_function(wrap_pyfunction!(process_numpy_array, m)?)?;
    Ok(())
}