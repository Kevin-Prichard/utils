#!/usr/bin/env node

import { readFileSync, existsSync } from 'node:fs';
import { hideBin } from 'yargs/helpers';
import yargs from 'yargs';

const argv = yargs(hideBin(process.argv))
    .parserConfiguration({"boolean-negation": true})
    .option('v', {
        alias: 'verbose',
        describe: 'Logs all values, not just types',
        default: false,
        type: 'boolean'})
    .option('s', {
        alias: 'sorted',
        describe: 'Sorts the output',
        default: true,
        type: 'boolean'})
    .option('k', {
        alias: 'keys',
        describe: 'Outputs a list of unique keys found',
        default: false,
        type: 'boolean'})
    .option('f', {
        alias: 'flatten',
        describe: 'Flatten array indexes to single value (by default "[]")',
        default: true,
        type: 'any'})
    .option('g', {
        alias: 'ignore',
        describe: 'Ignore and skip all keys matching this regex pattern',
        default: null,
        type: 'string'})
    .option('l', {
        alias: 'jsonl',
        describe: 'Expect JSONL in input files',
        default: false,
        type: 'boolean'})
    .parse();

const isObject = (v) => v && (typeof v === 'object') && !('length' in v);
const isArray = (v) => v && (typeof v === 'object') && ('length' in v);

const getJSONKeyPaths = (v, result=[], keyPath=[], keySet, verbose, indexRepl, ignore, depth) => {
    // let result = !_result ? [] : _result;
    // let keyPath = !_keyPath ? [] : _keyPath;
//    if (depth > 5) {
//        console.log("Depth", depth);
//    }

    if(isArray(v)) {
        for(let i=0; i<v.length; i++) {
            getJSONKeyPaths(
                v[i],
                result,
                keyPath.concat(indexRepl ? indexRepl : i),
                keySet,
                verbose,
                indexRepl,
                ignore,
                depth + 1,
            );
        }
    } else if(isObject(v)) {
        for(let k in v) {
            if (ignore && ignore.test(k))
                continue;
            keySet.add(k);
            getJSONKeyPaths(
                v[k],
                result,
                keyPath.concat(k),
                keySet,
                verbose,
                indexRepl,
                ignore,
                depth + 1,
            );
        }
    } else {
        let endPoint = keyPath.join('.') + ' = ' + (
            verbose ? JSON.stringify(v) : typeof(v)
        );
        result.add(endPoint);
    }
}

class UniqueCollection extends Set {
    push(v) {
        if(!this.has(v)) {
            super.add(v);
        }
    }
    sort() {
        return [...this].sort();
    }
}

// Run from CLI (i.e. not invoked via gulp)
if (import.meta.url === `file://${process.argv[1]}`) {
    if(argv._.length < 1) {
        console.log(
            'Requires at least one JSON file as argument.  ' +
            'Use --help for further information.');
        process.exit(1);
    }

    // Process each file
    let res = argv.sorted ? new UniqueCollection() : [];
    let keySet = new Set();
    let keyPath = [];
    const ignore = RegExp(argv.ignore);
//    console.log("ignore", ignore);
//    console.log('argv', argv);
//    console.log('argv._', argv._);
    for (let pathname of argv._) {
        if (!existsSync(pathname))
            continue;
//        console.log("pathname", pathname);
        let data = readFileSync(pathname, 'utf-8');
        if (argv.jsonl) {
            if (data.indexOf("\n") >= 0) {
                data = data.split("\n");
            }
        } else {
            data = [data]
        }
//        console.log(1);
        let line = 0;
        for (const [index, thisData] of data.entries()) {
//            console.log(index);
//            if(line % 2500) {
//                console.log(line++);
//            }
            if (thisData) {
                getJSONKeyPaths(
                    JSON.parse(thisData),
                    res,
                    keyPath,
                    keySet,
                    argv.verbose,
                    argv.flatten ?
                        typeof argv.flatten == 'string' ? argv.flatten : '[]'
                    : false,
                    ignore,
                    0,
                );
            }
        }
    }

    // Output results
    if(argv.sorted) {
        for (let r of res.sort()) {
            console.log(r);
        }
    } else {
        console.log(res.join('\n'));
    }

    // Output unique keys
    if(argv.keys) {
        if (argv.sorted) {
            keySet = [...keySet].sort();
        }
        for(let k of keySet) {
            console.log(k);
        }
    }
}

// Character strings to binary
// Array.from(new TextEncoder().encode('\x12\x02\b\x04'), bits=>bits.toString(2).padStart(8,'0'),).join('');
// t="";for(i=0;d='\x12\x02\b\x04'.charCodeAt(i/8);)t+=d>>(7-i++&7)&1
