#ifndef QIT_SORT_H

#include <vector>
#include <algorithm>

namespace qit {

template <typename T>
class SortIterator {
    public:
	typedef typename T::value_type value_type;
	SortIterator(T &iterator) {
        value_type value;
		while (iterator.next(value)) {
	        vector.push_back(value);
        }
		this->iterator = vector.begin();
		std::sort(vector.begin(), vector.end());
	}
	
	bool next(value_type &out) {
		if (iterator == vector.end()) {
		    return false;
		}
		out = *iterator;
		iterator++;
		return true;
	}

	void reset() {
		iterator = vector.begin();
	}

    protected:
    typename std::vector<value_type> vector;
    typename std::vector<value_type>::iterator iterator;
};

}

#endif // QIT_RANGE_H
